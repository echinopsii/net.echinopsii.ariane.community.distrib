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
import traceback
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
    def slack_notify(url, message, channel="#build", username="buildbot"):
        print("### Sending slack notification")
        payload = {"channel": channel, "username": username, "text": message}
        r = requests.post(url, data=json.dumps(payload))
        if r.status_code != 200:
            print("### Unable to send notification. Status code: {0}, Reason: {1}".format(r.status_code,
                                                                                          r.reason))

    @staticmethod
    def pluginmgr(args, script_path):
        #if args.add is not None:
        #    pass

        #elif args.list is True:
        if args.list is True:
            plugins = PluginRegistry(args.distribType, script_path).registry
            if len(plugins) != 0:
                print("\nAriane supported plugins list :\n")
                print('{:40} {:30} {:30}'.format("Ariane plugin name", "Ariane plugin version",
                                                 "Ariane distribution version"))
                print('{:40} {:30} {:30}'.format("------------------", "---------------------",
                                                 "---------------------------"))
                for plugin in plugins:
                    for pluginDist in plugin.distributions:
                            print('{:40} {:30} {:30}'.format(plugin.name, plugin.version, pluginDist))
            else:
                print("\nThere is currently no supported plugins for Ariane " + args.distribType +
                      " distrib... Coming soon !!!\n")

        elif args.list_plugin is not None:
            plugins = PluginRegistry(args.distribType, script_path).get_plugin(args.list_plugin[0])
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
            distrib = DistributionRegistry(args.distribType, script_path).get_distribution(args.list_distrib[0])
            if distrib is not None:
                od = distrib.get_supported_plugins()
                if len(od) != 0:
                    print("\nAriane supported plugins for distribution " + args.list_distrib[0] + " :\n")
                    print('{:40} {:30}'.format("Ariane plugin name", "Ariane plugin version"))
                    print('{:40} {:30}'.format("------------------", "---------------------"))
                    for pluginName in od.keys():
                        for addonVersion in od[pluginName]:
                            print('{:40} {:30}'.format(pluginName, addonVersion))
                else:
                    print("\nThere is currently no supported plugins for Ariane " + args.distribType +
                          " distrib... Coming soon !!!\n")
            else:
                print("Provided distribution " + args.list_distrib[0] + " is not valid")

        #elif args.remove is not None:
        #    pass

    @staticmethod
    def pluginpkgr(args, script_path):
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
            ForkRepo(args.distribType, script_path).fork_plugin(args.name)
        else:
            target_git_dir = os.path.abspath(tempfile.gettempdir() + "/ariane-plugins")

        build = "Plugin {0}, version {1}, dist_version: {2}, dist_type: {3}".format(args.name, args.version,
                                                                                    args.dversion, args.distribType)
        t = timeit.default_timer()
        try:
            SourcesManager(target_git_dir, args.distribType, args.dversion, script_path).\
                clone_plugin(user, password, args.name, args.version).compile_plugin(args.name, args.version)
        except RuntimeError as e:
            print("### Compilation failed")
            if args.slack:
                PluginCmd.slack_notify(args.slack, "Compilation failed for {0}".format(build))
            else:
                print("{0}".format(e))
            print(traceback.format_exc())
            return

        compile_time = round(timeit.default_timer()-t)
        compile_text = "Compilation successful for {0} in {1}s".format(build, compile_time)

        t = timeit.default_timer()
        try:
            Packager(target_git_dir, args.distribType, args.dversion, script_path, plugin_version=args.version).\
                build_plugin(args.name)
        except Exception as e:
            print("### Packaging failed: {0}".format(e))
            if args.slack:
                PluginCmd.slack_notify(args.slack, "{0}\nPackaging failed: {1}".format(compile_text, e))
            else:
                print("{0}".format(e))
            print(traceback.format_exc())
            return
        pack_time = round(timeit.default_timer()-t)

        if args.slack:
            PluginCmd.slack_notify(args.slack,
                                   "{0}\nPlugin successfully packaged in {1}s".format(compile_text, pack_time))