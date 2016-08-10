# distribution operations helper
#
# Copyright (C) 2014 Mathilde Ffrench
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from collections import OrderedDict
import json
import os

__author__ = 'mffrench'


class Distribution:

    def __init__(self, distrib_type, version, script_path):
        file_prefix_pattern = "ariane." + distrib_type + ".distrib"
        self.script_path = script_path
        self.version = version
        self.name = file_prefix_pattern + "-" + self.version
        self.distrib_file = self.script_path+"/resources/distrib/" + self.name + ".json"
        self.addons_file = self.script_path+"/resources/plugins/ariane." + distrib_type + ".plugins-distrib-" + \
            self.version + ".json"
        self.maven_file = self.script_path+"/resources/maven/pom-" + file_prefix_pattern + "-" + version + ".xml"

    def is_valid(self):
        if os.path.exists(self.distrib_file) and os.path.exists(self.maven_file):
            return True
        else:
            return False

    def details(self):
        return OrderedDict(sorted(json.load(open(self.distrib_file)).items(), key=lambda t: t[0]))

    def get_supported_plugins(self):
        if os.path.exists(self.addons_file):
            return OrderedDict(sorted(json.load(open(self.addons_file)).items(), key=lambda t: t[0]))
        else:
            return None

    def remove(self):
        os.remove(self.distrib_file)
        os.remove(self.maven_file)
        if os.path.exists(self.addons_file):
            os.remove(self.addons_file)



