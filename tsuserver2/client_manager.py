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
from tsuserver2.client import Client


class ClientManager:
    def __init__(self):
        self.clients = set()

    def new_client(self, transport):
        cl = Client(transport)
        self.clients.add(cl)
        return cl

    def disconnect_client(self, client, msg):
        logging.log_debug(msg, client)
        client.close_transport()
        try:
            self.clients.remove(client)
            client.area.remove_client(client)
        except ValueError:
            return
