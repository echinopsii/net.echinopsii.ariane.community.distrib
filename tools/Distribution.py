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

    def __init__(self, distribType, version):
        filePrefixPattern = "ariane." + distribType + ".distrib"
        self.version = version
        self.name = filePrefixPattern + "-" + self.version
        self.distribFile = "resources/distrib/" + self.name + ".json"
        self.addonsFile = "resources/plugins/ariane." + distribType + ".plugins-distrib-" + self.version + ".json"
        self.mavenFile = "resources/maven/pom-" + filePrefixPattern + "-" + version + ".xml"

    def isValid(self):
        if os.path.exists(self.distribFile) and os.path.exists(self.mavenFile):
            return True
        else:
            return False

    def details(self):
        return OrderedDict(sorted(json.load(open(self.distribFile)).items(), key=lambda t: t[0]))

    def getSupportedPlugins(self):
        if os.path.exists(self.addonsFile):
            return OrderedDict(sorted(json.load(open(self.addonsFile)).items(), key=lambda t: t[0]))
        else:
            return None

    def remove(self):
        os.remove(self.distribFile)
        os.remove(self.mavenFile)
        if os.path.exists(self.addonsFile):
            os.remove(self.addonsFile)



