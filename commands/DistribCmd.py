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
from tools.ForkRepo import ForkRepo
import requests
import json
import timeit

__author__ = 'mffrench'


class DistribCmd:
    
    @staticmethod
    def slack_notify(url,message,channel="#build",username="buildbot"):
        print("### Sending slack notification")
        payload={"channel": channel, "username": username, "text" : message }
        r=requests.post(url,data=json.dumps(payload))
        if r.status_code!=200:
            print("### Unable to send notification. Status code: {0}, Reason: {1}".format(r.status_code,r.reason))


    @staticmethod
    def distmgr(args,scriptPath):
        if args.details is not None:
            distrib = DistributionRegistry(args.distribType,scriptPath).getDistribution(args.details[0])
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
            distribRegistry = DistributionRegistry(args.distribType,scriptPath=scriptPath)
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
    def dispkgr(args,scriptPath):
        if args.distribType != "community":
            if ":" in args.user:
                user=args.user.split(':')[0]
                password=args.user.split(':')[1]
            else:
                user=args.user
                password = getpass.getpass("Stash password : ")
        else:
            user = None
            password = None

        if args.version == "master.SNAPSHOT":
            targetGitDir = '/'.join(scriptPath.split('/')[:-1])
            ForkRepo(args.distribType,scriptPath).forkCore()
        else:
            targetGitDir = tempfile.TemporaryDirectory("ariane-distrib-" + args.version).name

        build="Distribution Version: {0}, Distribution Type: {1}".format(args.version,args.distribType)
        t=timeit.default_timer()
        try:
            SourcesManager(targetGitDir, args.distribType, args.version,scriptPath).cloneCore(user, password).compileCore()
        except RuntimeError as e:
            print("### Compilation failed")
            if args.slack:
                DistribCmd.slack_notify(args.slack,"Compilation failed for {0}".format(build))
            else:
                print("{0}".format(e))
            return

        compileTime=round(timeit.default_timer()-t)
        compileText="Compilation successful for {0} in {1}s".format(build,compileTime)

        t=timeit.default_timer()
        try:
            Packager(targetGitDir, args.distribType, args.version, scriptPath).buildDistrib()
        except Exception as e:
            print("### Packaging failed")
            if args.slack:
                DistribCmd.slack_notify(args.slack,"{0}\nPackaging failed: {1}".format(compileText,e))
            else:
                print("{0}".format(e))

            return
        packTime=round(timeit.default_timer()-t)

        if args.slack:
            DistribCmd.slack_notify(args.slack,"{0}\nDistribution successfully packaged in {1}s".format(compileText,packTime))
