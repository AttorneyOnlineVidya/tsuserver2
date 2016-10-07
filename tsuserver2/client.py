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

from tsuserver2 import logging


class Client:
    def __init__(self, transport):
        self._transport = transport
        self.software = None
        self.version = None
        self.area = None
        self.charid = -1
        self.is_mod = False

    def send_raw_message(self, msg):
        bytes_msg = bytes(msg, 'UTF-8')
        logging.log_debug('[SEND]' + str(bytes_msg), self)
        self._transport.write(bytes_msg)

    def send_command(self, cmd, *args):
        res = str(cmd)
        for arg in args:
            res += '#' + str(arg)
        res += '#%'
        self.send_raw_message(res)

    def get_ip(self):
        return self._transport.get_extra_info('peername')[0]

    def close_transport(self):
        self._transport.close()
