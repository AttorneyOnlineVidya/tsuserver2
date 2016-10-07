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

from tsuserver2.config import areas


class AreaManager:
    def __init__(self):
        self.areas = areas.CFG_AREAS
        self.default_area = areas.CFG_DEFAULT_AREA

    def change_client_area(self, client, target_area):
        if target_area.is_charid_taken(client.charid):
            raise Exception('Character already taken in that area.')  # todo randomchar
        if client.area is not None:
            client.area.remove_client(client)
        target_area.add_client(client)
        client.area = target_area

    def reload_areas(self):
        # todo move characters temporarily etc
        self.areas = areas.CFG_AREAS
        self.default_area = areas.CFG_DEFAULT_AREA

    def get_area_by_id(self, id):
        try:
            area = self.areas[id]
        except IndexError:
            raise
        return area
