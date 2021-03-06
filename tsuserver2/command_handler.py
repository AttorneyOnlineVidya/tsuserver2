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


class CommandHandler:
    def __init__(self, server):
        self._server = server

    def dispatch_command(self, client, cmd, args):
        try:
            self.cmd_dispatcher[cmd](self, client, args)
        except KeyError:
            logging.log_debug('Invalid command {}'.format(cmd), client)

    def cmd_motd(self, client, args):
        pass  # todo

    cmd_dispatcher = {
        'motd': cmd_motd
    }
