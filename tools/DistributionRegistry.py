# Ariane distribution registry operations helper
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
import fnmatch
import os
from tools.Distribution import Distribution

__author__ = 'mffrench'


class DistributionRegistry:

    def __init__(self, distribType,scriptPath):
        self.registry = []
        self.scriptPath=scriptPath

        filePrefixPattern = "ariane." + distribType + ".distrib"
        for file in os.listdir(self.scriptPath+"/resources/distrib/"):
            filematch = filePrefixPattern + "*json"
            if fnmatch.fnmatch(file, filematch):
                splitmatch= filePrefixPattern+"-"
                distribVersion = file.split(".json")[0].split(splitmatch)[1]
                distribution = Distribution(distribType, distribVersion,self.scriptPath)
                if distribution.isValid():
                    self.registry.append(distribution)

    def getDistribution(self, version):
        for distribution in self.registry:
            if distribution.version == version:
                return distribution
        return None

    @staticmethod
    def printInvalidDistributions():
        pass

    @staticmethod
    def removeInvalidDistributions():
        pass
