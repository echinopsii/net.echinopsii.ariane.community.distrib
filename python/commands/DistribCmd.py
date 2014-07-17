# Ariane distribution commands
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

import getpass
import os
import tempfile
from tools.DistributionRegistry import DistributionRegistry
from tools.Packager import Packager
from tools.SourcesManager import SourcesManager

__author__ = 'mffrench'


class DistribCmd:

    @staticmethod
    def distmgr(args):
        if args.details is not None:
            distrib = DistributionRegistry(args.distribType).getDistribution(args.details[0])
            if distrib is not None:
                details = distrib.details()
                print("\nDetails of Ariane distribution " + args.details[0] + " :\n")
                print('{:40} {:20}'.format("Ariane component name", "Ariane component version"))
                print('{:40} {:20}'.format("---------------------", "------------------------"))
                for key in details.keys():
                    print('{:40} {:20}'.format(key, details[key]))

            else:
                print("Provided distribution version " + args.details[0] + " is not valid")

        elif args.list is True:
            print("\nList of Ariane distribution :\n")
            distribRegistry = DistributionRegistry(args.distribType)
            for distribution in distribRegistry.registry:
                print(distribution.name)

        #elif args.remove is not None:
        #    distribRegistry = ccDistributionRegistry()
        #    distrib = distribRegistry.getDistribution(args.remove[0])
        #    if distrib is not None:
        #        distrib.remove()
        #    else:
        #        print("Provided distribution version " + args.remove[0] + " is not valid")

    @staticmethod
    def dispkgr(args):
        if args.distribType != "community":
            user = args.user
            password = getpass.getpass("Stash password : ")
        else:
            user = None
            password = None

        if args.version == "master.SNAPSHOT":
            targetGitDir = os.path.abspath("../../")
        else:
            targetGitDir = tempfile.TemporaryDirectory("ariane-distrib-" + args.version).name

        SourcesManager(targetGitDir, args.distribType, args.version).cloneCore(user, password).compileCore()
        Packager(targetGitDir, args.distribType, args.version).buildDistrib()