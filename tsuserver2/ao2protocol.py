# tsuserver2, an Attorney Online 2 server
#
# Copyright (C) 2016 tsukasa84 <tsukasadev84@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio

from tsuserver2 import logging
from tsuserver2.config import characters
from tsuserver2.config import config


class AO2Protocol(asyncio.Protocol):
    def __init__(self, server):
        self._server = server
        self._client = None
        self._buffer = ""

    def connection_made(self, transport):
        self._client = self._server.client_manager.new_client(transport)
        self._server.area_manager.change_client_area(self._client, self._server.area_manager.default_area)
        logging.log_debug('New connection.', self._client)

        self._client.send_command('HI', config.CFG_SOFTWARE, config.CFG_VERSION)
        self.net_send_all_ta()

    def connection_lost(self, exc):
        if exc is None:
            exc = 'Disconnected.'
        self._server.client_manager.disconnect_client(self._client, str(exc))

    def data_received(self, data):
        logging.log_debug('[RECV]' + str(data), self._client)
        raw_msg = str(data, 'UTF-8')
        for cmd, args in self.receive_cmds(raw_msg):
            self.process_command(cmd, args)

    def receive_cmds(self, msg):
        msg = self._buffer + msg
        # message is way too long
        if len(msg) > 32000:
            self._server.client_manager.disconnect_client(self._client, 'Message too long.')
        while '#%' in msg:
            cmd, rest = msg.split('#%', 1)
            split_cmd, *args = cmd.split('#')
            yield split_cmd, args
            msg = rest
        self._buffer = msg

    def process_command(self, cmd, args):
        try:
            self.net_cmd_dispatcher[cmd](self, args)
        except KeyError:
            logging.log_debug('[EXCEPTION]Invalid command received.; CMD:{}; ARGS:{}'.format(cmd, args), self._client)
        except Exception as e:
            logging.log_debug('[EXCEPTION]{}; CMD:{}; ARGS:{}'.format(e, cmd, args), self._client)

    def net_send_done(self):
        """
        'DONE' - sends DONE, effectively taking the client to the char. select screen
        """
        self._client.send_command('DONE')

    def net_send_tc(self):
        """
        'TC' - sends a list of taken characters
        TC#n0#n1#...#n#%
        0 - normal
        1 - taken
        2 - passworded
        3 - taken and passworded
        """
        out_flags = []
        for i, char in enumerate(characters.CFG_CHARLIST):
            flag = 0
            if self._client.area.is_charid_taken(i):
                flag += 1
            pw = char[2]
            if pw != '':
                flag += 2
            out_flags.append(flag)
        self._client.send_command('TC', *out_flags)

    def net_send_all_ta(self):
        """
        Sends every client updated area player count information.
        """
        for client in self._server.client_manager.clients:
            client.update_area_list(self._server.area_manager.areas)

    def net_cmd_hi(self, args):
        """
        'HI' - the initial handshake
        sends HI#software#version#%
        :param args:
        software - string
        version - string
        """
        # todo check for bans
        # todo server client limit
        if len(args) != 2:
            raise Exception('HI should only have 2 arguments.')
        if self._client.software is not None or self._client.version is not None:
            raise Exception('User already passed handshake.')
        self._client.software = args[0]
        self._client.version = args[1]
        self._client.send_command('PN', len(self._server.client_manager.clients), config.CFG_PLAYERLIMIT)

    def net_cmd_rc(self, args):
        """
        'RC' - request character list
        sends a string in the format SC#character&desc#...#%
        :param args: none
        """
        if len(args) != 0:
            raise Exception('RC should not have any arguments.')
        out_chars = []
        for char in characters.CFG_CHARLIST:
            name, desc, _ = char
            out_chars.append('{}&{}'.format(name, desc))
        self._client.send_command('SC', *out_chars)
        self.net_send_tc()
        self.net_send_done()

    def net_cmd_rm(self, args):
        """
        'RM' - request music list
        sends a string in the format SM#song1.mp3#song2.mp3#...#%
        :param args: none
        """
        if len(args) != 0:
            raise Exception('RM should not have any arguments.')
        self._client.send_command('SM', *self._server.songlist)

    def net_cmd_ra(self, args):
        """
        'RA' - requests area list
        sends a string in the format SA#name&background&passworded#...#%
        passworded can be either 0 or 1
        :param args: none
        """
        if len(args) != 0:
            raise Exception('RA should not have any arguments.')
        out_area_info = []
        out_area_players = []
        for area in self._server.area_manager.areas:
            pw_flag = 0
            if area.password != '':
                pw_flag = 1
            out_area_info.append('{}&{}&{}'.format(area.name, area.background, pw_flag))
            out_area_players.append(len(area.clients))
        self._client.send_command('SA', *out_area_info)
        self._client.send_command('TA', *out_area_players)

    def net_cmd_uc(self, args):
        """
        'UC' - pick a character
        sends a string in the format OC#charid#flag#%
        flag can be:
        0 - ok
        1 - char is already taken
        2 - wrong password
        3 - ok + give mod privileges
        :param args:
        charid - int
        password - string
        """
        if len(args) != 2:
            raise Exception('UC should have 2 arguments.')
        charid_s, pw = args
        flag = 0
        try:
            charid = int(charid_s)
        except ValueError:
            raise Exception('Character ID must be a number.')
        try:
            taken = self._client.area.is_charid_taken(charid)
        except:
            raise
        if taken:
            flag = 1
        else:
            if pw == config.CFG_MODPASS:
                self._client.is_mod = True
                flag = 3
            elif characters.CFG_CHARLIST[charid][2] != '' and pw != characters.CFG_CHARLIST[charid][2]:
                flag = 2
        if flag == 0 or flag == 3:
            self._client.charid = charid
        self._client.send_command('OC', charid, flag)

    def net_cmd_fc(self, args):
        """
        'FC' - free character
        :param args: none
        """
        if len(args) != 0:
            raise Exception('FC should not have any arguments.')
        self._client.charid = -1
        self.net_send_tc()
        self.net_send_done()

    def net_cmd_aa(self, args):
        """
        'AA' - join an area
        sends OA#areaid#modifier#%, where modifier is either 0 (ok) or 1 (bad password)
        afterwards sends TA (area player count) to every client
        :param args:
        0 - area ID
        1 - password
        """
        if len(args) != 2:
            raise Exception('AA should have 2 arguments.')

        idx_s, pw = args

        try:
            idx = int(idx_s)
        except ValueError:
            raise Exception('Area ID must be an integer.')

        try:
            area = self._server.area_manager.get_area_by_id(idx)
        except IndexError:
            raise

        if not self._client.is_mod and (area.password != '' and pw != area.password):
            self._client.send_command('OA', idx, 1)
            return

        try:
            self._server.area_manager.change_client_area(self._client, area)
        except:
            raise

        # confirm area switch
        self._client.send_command('OA', idx, 0)
        # update everyone's area player counts
        self.net_send_all_ta()

    def net_cmd_mc(self, args):
        pass

    def net_cmd_ms(self, args):
        pass

    # OOC message
    def net_cmd_ct(self, args):
        # TODO ooc commands
        # self._server.process_command(self._client, cmd, args)
        pass

    def net_cmd_zz(self, args):
        pass

    net_cmd_dispatcher = {
        'HI': net_cmd_hi,  # handshake
        'RC': net_cmd_rc,  # request chars
        'RM': net_cmd_rm,  # request music
        'RA': net_cmd_ra,  # request areas
        'UC': net_cmd_uc,  # pick character
        'FC': net_cmd_fc,  # free character
        'AA': net_cmd_aa,  # change area
        'MC': net_cmd_mc,  # play music
        'MS': net_cmd_ms,  # ic message
        'CT': net_cmd_ct,  # ooc message
        'ZZ': net_cmd_zz,  # call mod
    }
