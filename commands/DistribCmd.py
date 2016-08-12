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
import tempfile
import traceback
import sys
from tools.Distribution import Distribution
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
    def slack_notify(url, message, channel="#build", username="buildbot"):
        print("### Sending slack notification")
        payload = {"channel": channel, "username": username, "text": message}
        r = requests.post(url, data=json.dumps(payload))
        if r.status_code != 200:
            print("### Unable to send notification. Status code: {0}, Reason: {1}".format(r.status_code, r.reason))

    @staticmethod
    def distmgr(args, script_path):
        if args.details is not None:
            if args.details.__len__() > 1:
                distrib = DistributionRegistry(args.distribType, script_path).get_distribution(
                    args.details[0], args.details[1]
                )
                dep_type = args.details[1]
            else:
                distrib = DistributionRegistry(args.distribType, script_path).get_distribution(args.details[0])
                dep_type = Distribution.MNO_DEPLOYMENT_TYPE

            if distrib is not None:
                details = distrib.details()
                print("\nDetails of Ariane distribution " + dep_type + ":" + args.details[0] + " :\n")

                print('{:40} {:30} {:30}'.format("Ariane component name", "Ariane component version",
                                                 "Ariane component branch"))
                print('{:40} {:30} {:30}'.format("---------------------", "------------------------",
                                                 "------------------------"))
                for key in details.keys():
                    print('{:40} {:30} {:30}'.format(
                        key,
                        details[key].split(".")[1] if details[key].split(".SNAP").__len__() > 1 else details[key],
                        details[key].split(".")[0] if details[key].split(".SNAP").__len__() > 1 else "TAG")
                    )

            else:
                print("Provided distribution version " + args.details[0] + " is not valid")

        elif args.list is True:
            print("\nList of Ariane distribution :\n")
            distrib_registry = DistributionRegistry(args.distribType, script_path=script_path)
            for distribution in distrib_registry.registry:
                print(distribution.name)

        #elif args.remove is not None:
        #    distribRegistry = ccDistributionRegistry()
        #    distrib = distribRegistry.getDistribution(args.remove[0])
        #    if distrib is not None:
        #        distrib.remove()
        #    else:
        #        print("Provided distribution version " + args.remove[0] + " is not valid")

    @staticmethod
    def dispkgr(args, script_path):
        if args.distribType != "community":
            if ":" in args.user:
                user = args.user.split(':')[0]
                password = args.user.split(':')[1]
            else:
                user = args.user
                password = getpass.getpass("Stash password : ")
        else:
            user = None
            password = None

        if 'SNAPSHOT' in args.version:
            target_git_dir = '/'.join(script_path.split('/')[:-1])
            ForkRepo(args.distribType, script_path).fork_core()
        else:
            target_git_dir = tempfile.TemporaryDirectory("ariane-distrib-" + args.version).name

        build = "Distribution Version: {0}, Distribution Type: {1}".format(args.version, args.distribType)
        t = timeit.default_timer()
        try:
            SourcesManager(target_git_dir, args.distribType, args.distribDepType, args.version, script_path).\
                clone_core(user, password).\
                compile_core()
        except RuntimeError as e:
            print("### Compilation failed")
            if args.slack:
                DistribCmd.slack_notify(args.slack, "Compilation failed for {0}".format(build))
            else:
                print("{0}".format(e))
            print(traceback.format_exc())
            sys.exit(-1)

        compile_time = round(timeit.default_timer()-t)
        compile_text = "Compilation successful for {0} in {1}s".format(build, compile_time)

        t = timeit.default_timer()
        try:

            Packager(target_git_dir, args.distribType, args.version, args.distribDepType, script_path).build_distrib()
        except Exception as e:
            print("### Packaging failed")
            if args.slack:
                DistribCmd.slack_notify(args.slack, "{0}\nPackaging failed: {1}".format(compile_text, e))
            else:
                print("{0}".format(e))
            print(traceback.format_exc())

            return
        pack_time = round(timeit.default_timer()-t)

        if args.slack:
            DistribCmd.slack_notify(args.slack, "{0}\nDistribution successfully packaged in {1}s".
                                    format(compile_text, pack_time))
