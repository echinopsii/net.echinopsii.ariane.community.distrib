# distribution parser
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

import argparse
from commands.PluginCmd import PluginCmd
from commands.DistribCmd import DistribCmd
from commands.GitCmd import GitCmd


__author__ = 'mffrench'


class Parser:

    def __init__(self, distribType):
        self.distribType = distribType


    def parse(self):
        parser = argparse.ArgumentParser(description='Ariane distribution manager')
        mainSubParsers = parser.add_subparsers(help="sub commands help summary")

        parserAddonMgr = mainSubParsers.add_parser(name="pluginmgr", description="Manage supported Ariane plugins", help="[-h] (-l | -la plugin_name | -ld distribution_version)")
        meGroupAddonMgr = parserAddonMgr.add_mutually_exclusive_group(required=True)
        #meGroupAddonMgr.add_argument("-a",  "--add", help="Add a supported plugin", nargs=3, metavar=("plugin_name", "plugin_version", "distrib_version"))
        meGroupAddonMgr.add_argument("-l",  "--list", help="List all supported plugins versions and distributions", action="store_true")
        meGroupAddonMgr.add_argument("-la", "--list-plugin", help="List supported plugin versions and distributions", nargs=1, metavar="plugin_name")
        meGroupAddonMgr.add_argument("-ld", "--list-distrib", help="List supported plugins for a distribution version", nargs=1, metavar="distribution_version")
        #meGroupAddonMgr.add_argument("-r",  "--remove", help="Remove a supported plugin", nargs=3, metavar=("plugin_name", "plugin_version", "distrib_version"))
        parserAddonMgr.add_argument("distribType", action='store_const', const=self.distribType, help=argparse.SUPPRESS)
        parserAddonMgr.set_defaults(func=PluginCmd.pluginmgr)

        if self.distribType != "community":
            parserAddonPkgr = mainSubParsers.add_parser(name="pluginpkgr", description="Package a supported Ariane plugin", help="[-h] user name version")
        else:
            parserAddonPkgr = mainSubParsers.add_parser(name="pluginpkgr", description="Package a supported Ariane plugin", help="[-h] name version")

        if self.distribType != "community":
            parserAddonPkgr.add_argument("user", help="Stash username")

        parserAddonPkgr.add_argument("name", help="Ariane plugin name to package")
        parserAddonPkgr.add_argument("version", help="Ariane plugin version to package")
        parserAddonPkgr.add_argument("distribType", action='store_const', const=self.distribType, help=argparse.SUPPRESS)
        parserAddonPkgr.set_defaults(func=PluginCmd.pluginpkgr)

        parserDistributionMgr = mainSubParsers.add_parser(name="distmgr", description="Manage supported Ariane distributions version", help="[-h] (-d distribution_version | -l)")
        meGroupDistributionMgr = parserDistributionMgr.add_mutually_exclusive_group(required=True)
        #meGroupDistributionMgr.add_argument("-a", "--add", help="Add a supported distribution version", nargs=1)
        meGroupDistributionMgr.add_argument("-d", "--details", help="Show supported distribution details", nargs=1)
        meGroupDistributionMgr.add_argument("-l", "--list", help="List supported distribution version", action="store_true")
        #meGroupDistributionMgr.add_argument("-r", "--remove", help="Remove a supported distribution version", nargs=1)
        parserDistributionMgr.add_argument("distribType", action='store_const', const=self.distribType, help=argparse.SUPPRESS)
        parserDistributionMgr.set_defaults(func=DistribCmd.distmgr)

        if self.distribType != "community":
            parserDistributionPkgr = mainSubParsers.add_parser(name="distpkgr", description="Package a distribution", help="[-h] user version")
        else:
            parserDistributionPkgr = mainSubParsers.add_parser(name="distpkgr", description="Package a distribution", help="[-h] version")
        if self.distribType != "community":
            parserDistributionPkgr.add_argument("user", help="Stash username")
        parserDistributionPkgr.add_argument("version", help="Ariane distribution version to package")
        parserDistributionPkgr.add_argument("distribType", action='store_const', const=self.distribType, help=argparse.SUPPRESS)
        parserDistributionPkgr.set_defaults(func=DistribCmd.dispkgr)

        if self.distribType != "community":
            parserAddGitRepo = mainSubParsers.add_parser(name="gitadd", description="Add a new Ariane git repository", help="[-h] name url {plugin,core}")
            parserAddGitRepo.add_argument("name", help="Ariane git repository name")
            parserAddGitRepo.add_argument("url", help="Ariane git repository url")
            parserAddGitRepo.add_argument("type", help="Specifiy if target git repository is a Ariane core component or a Ariane plugin", choices=["plugin", "core"])
            parserAddGitRepo.set_defaults(func=GitCmd.gitAdd)

            parserGitBranch = mainSubParsers.add_parser(name="gitbranch", description="List existing branch of a git repository", help="[-h] user name")
            parserGitBranch.add_argument("user", help="Stash username")
            parserGitBranch.add_argument("name", help="Ariane git repository name")
            parserGitBranch.set_defaults(func=GitCmd.gitBranch)

            parserListGitRepo = mainSubParsers.add_parser(name="gitlist", description="List Ariane git repositories", help="[-h] [-a | -c]")
            meGroupListGitRepo = parserListGitRepo.add_mutually_exclusive_group()
            meGroupListGitRepo.add_argument("-a", "--plugin", help="list Ariane plugin repositories only", action="store_true")
            meGroupListGitRepo.add_argument("-c", "--core", help="list Ariane core repositories only", action="store_true")
            parserListGitRepo.set_defaults(func=GitCmd.gitList)

            parserRemoveGitRepo = mainSubParsers.add_parser(name="gitremove", description="Remove a Ariane git repository", help="[-h] name")
            parserRemoveGitRepo.add_argument("name", help="Ariane git repository name to remove")
            parserRemoveGitRepo.set_defaults(func=GitCmd.gitRemove)

            parserGitTag = mainSubParsers.add_parser(name="gittag", description="List existing tag of a git repository", help="[-h] user name")
            parserGitTag.add_argument("user", help="Stash username")
            parserGitTag.add_argument("name", help="Ariane git repository name")
            parserGitTag.set_defaults(func=GitCmd.gitTag)

        return parser.parse_args()
