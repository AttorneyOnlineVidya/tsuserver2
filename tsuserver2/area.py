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

from tsuserver2.config import characters


class Area:
    def __init__(self, name, background, bg_lock, password):
        self.clients = set()
        self.name = name
        self.background = background
        self.bg_lock = bg_lock
        self.password = password

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def is_charid_taken(self, id):
        if id < 0 or id >= len(characters.CFG_CHARLIST):
            if id == -1:
                return False
            raise Exception('Invalid character ID.')
        for client in self.clients:
            if client.charid == id:
                return True
        return False
