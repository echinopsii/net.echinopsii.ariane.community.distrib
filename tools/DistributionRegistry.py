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

    def __init__(self, distrib_type, script_path):
        self.registry = []
        self.script_path = script_path

        file_prefix_pattern = "ariane." + distrib_type + ".distrib"
        for file in os.listdir(self.script_path+"/resources/distrib/"):
            file_match = file_prefix_pattern + "*json"
            if fnmatch.fnmatch(file, file_match):
                split_match = file_prefix_pattern+"-"
                distrib_version = file.split(".json")[0].split(split_match)[1]
                distribution = Distribution(distrib_type, distrib_version, self.script_path)
                if distribution.is_valid():
                    self.registry.append(distribution)

    def get_distribution(self, version):
        for distribution in self.registry:
            if distribution.version == version:
                return distribution
        return None

    @staticmethod
    def print_invalid_distributions():
        pass

    @staticmethod
    def remove_invalid_distributions():
        pass
