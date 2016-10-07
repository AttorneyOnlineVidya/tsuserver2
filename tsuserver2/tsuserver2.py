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
from tsuserver2.ao2protocol import AO2Protocol
from tsuserver2.area_manager import AreaManager
from tsuserver2.client_manager import ClientManager
from tsuserver2.command_handler import CommandHandler
from tsuserver2.config import songlist


class TsuServer2:
    def __init__(self):
        self.client_manager = ClientManager(self)
        self.area_manager = AreaManager()
        self.cmd_handler = CommandHandler(self)
        self.songlist = songlist.CFG_SONGLIST

    def start(self):
        logging.log_debug('Starting server')
        loop = asyncio.get_event_loop()
        cr = loop.create_server(lambda: AO2Protocol(self), None, 50000)
        srv = loop.run_until_complete(cr)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.close()

    def reload_songlist(self):
        self.songlist = songlist.CFG_SONGLIST

    def reload_arealist(self):
        self.area_manager.reload_areas()
