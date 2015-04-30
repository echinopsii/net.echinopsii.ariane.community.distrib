# Ariane addon commands
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
from tools.PluginRegistry import PluginRegistry
from tools.DistributionRegistry import DistributionRegistry
from tools.Packager import Packager
from tools.SourcesManager import SourcesManager
from tools.ForkRepo import ForkRepo
import timeit
import json
import requests

__author__ = 'mffrench'


class PluginCmd:

    @staticmethod
    def slack_notify(url,message,channel="#build",username="buildbot"):
        print("### Sending slack notification")
        payload={"channel": channel, "username": username, "text" : message }
        r=requests.post(url,data=json.dumps(payload))
        if r.status_code!=200:
            print("### Unable to send notification. Status code: {0}, Reason: {1}".format(r.status_code,r.reason))


    @staticmethod
    def pluginmgr(args,scriptPath):
        #if args.add is not None:
        #    pass

        #elif args.list is True:
        if args.list is True:
            plugins = PluginRegistry(args.distribType,scriptPath).registry
            if len(plugins) != 0:
                print("\nAriane supported plugins list :\n")
                print('{:40} {:30} {:30}'.format("Ariane plugin name", "Ariane plugin version", "Ariane distribution version"))
                print('{:40} {:30} {:30}'.format("------------------", "---------------------", "---------------------------"))
                for plugin in plugins:
                    for pluginDist in plugin.distributions:
                            print('{:40} {:30} {:30}'.format(plugin.name, plugin.version, pluginDist))
            else:
                print("\nThere is currently no supported plugins for Ariane " + args.distribType + " distrib... Coming soon !!!\n")

        elif args.list_plugin is not None:
            plugins = PluginRegistry(args.distribType,scriptPath).getPlugin(args.list_plugin[0])
            if plugins is not None:
                print("\nAriane " + args.list_plugin[0] + " supported plugin versions and distributions list :\n")
                print('{:30} {:30}'.format("Ariane plugin version", "Ariane distribution version"))
                print('{:30} {:30}'.format("---------------------", "---------------------------"))
                for plugin in plugins:
                    for pluginDist in plugin.distributions:
                        print('{:30} {:30}'.format(plugin.version, pluginDist))
            else:
                print("Provided addon " + args.list_plugin[0] + " is not valid")

        elif args.list_distrib is not None:
            distrib = DistributionRegistry(args.distribType,scriptPath).getDistribution(args.list_distrib[0])
            if distrib is not None:
                od = distrib.getSupportedPlugins()
                if len(od) != 0:
                    print("\nAriane supported plugins for distribution " + args.list_distrib[0] + " :\n")
                    print('{:40} {:30}'.format("Ariane plugin name", "Ariane plugin version"))
                    print('{:40} {:30}'.format("------------------", "---------------------"))
                    for pluginName in od.keys():
                        for addonVersion in od[pluginName]:
                            print('{:40} {:30}'.format(pluginName, addonVersion))
                else:
                    print("\nThere is currently no supported plugins for Ariane " + args.distribType + " distrib... Coming soon !!!\n")
            else:
                print("Provided distribution " + args.list_distrib[0] + " is not valid")

        #elif args.remove is not None:
        #    pass

    @staticmethod
    def pluginpkgr(args,scriptPath):
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
            ForkRepo(args.distribType,scriptPath).forkPlugin(args.name)
        else:
            targetGitDir = os.path.abspath(tempfile.gettempdir() + "/ariane-plugins")

        build="Plugin {0}, version {1}, dist_version: {2}, dist_type: {3}".format(args.name,args.version,args.dversion,args.distribType)
        t=timeit.default_timer()
        try:
            SourcesManager(targetGitDir, args.distribType, args.dversion, scriptPath).clonePlugin(user, password, args.name, args.version).compilePlugin(args.name, args.version)
        except RuntimeError as e:
            print("### Compilation failed")
            if args.slack:
                PluginCmd.slack_notify(args.slack,"Compilation failed for {0}".format(build))
            return

        compileTime=round(timeit.default_timer()-t)
        compileText="Compilation successful for {0} in {1}s".format(build,compileTime)

        t=timeit.default_timer()
        try:
            Packager(targetGitDir, args.distribType, args.version, scriptPath).buildPlugin(args.name)
        except Exception as e:
            print("### Packaging failed: {0}".format(e))
            if args.slack:
                PluginCmd.slack_notify(args.slack,"{0}\nPackaging failed: {1}".format(compileText,e))
            return
        packTime=round(timeit.default_timer()-t)

        if args.slack:
            PluginCmd.slack_notify(args.slack,"{0}\nPlugin successfully packaged in {1}s".format(compileText,packTime))

