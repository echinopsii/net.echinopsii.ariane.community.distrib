# Ariane addon registry operations helper
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
from tools.Plugin import Plugin
import os

__author__ = 'mffrench'


class PluginRegistry:

    def __init__(self, distribType, scriptPath):
        self.registry = []
        self.scriptPath = scriptPath
        od = OrderedDict(sorted(json.load(open(self.scriptPath+"/resources/plugins/ariane." + distribType + ".plugins.json")).items(), key=lambda t: t[0]))
        for key in od.keys():
            pluginName = key
            for pluginDesc in od[key]:
                pluginVersion = pluginDesc["pluginVersion"]
                pluginDistribs = pluginDesc["distVersion"]
                self.registry.append(Plugin(pluginName, pluginVersion, pluginDistribs))

    def getPlugin(self, name):
        ret = None
        for addon in self.registry:
            if addon.name == name:
                if ret is None:
                    ret = []
                ret.append(addon)
        return ret
