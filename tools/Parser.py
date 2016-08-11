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

    def __init__(self, distrib_type):
        self.distrib_type = distrib_type

    def parse(self):
        parser = argparse.ArgumentParser(description='Ariane distribution manager')
        parser.add_argument("-s", "--slack", default=None, help="Slack url for notification")

        main_sub_parsers = parser.add_subparsers(help="sub commands help summary")

        parser_addon_mgr = main_sub_parsers.add_parser(name="pluginmgr", description="Manage supported Ariane plugins",
                                                       help="[-h] (-l | -la plugin_name | -ld distribution_version)")
        me_group_addon_mgr = parser_addon_mgr.add_mutually_exclusive_group(required=True)
        # meGroupAddonMgr.add_argument("-a",  "--add", help="Add a supported plugin", nargs=3,
        # metavar=("plugin_name", "plugin_version", "distrib_version"))
        me_group_addon_mgr.add_argument("-l",  "--list", help="List all supported plugins versions and distributions",
                                        action="store_true")
        me_group_addon_mgr.add_argument("-la", "--list-plugin", help="List supported plugin versions and distributions",
                                        nargs=1, metavar="plugin_name")
        me_group_addon_mgr.add_argument("-ld", "--list-distrib",
                                        help="List supported plugins for a distribution version",
                                        nargs=1, metavar="distribution_version")
        # meGroupAddonMgr.add_argument("-r",  "--remove", help="Remove a supported plugin", nargs=3,
        # metavar=("plugin_name", "plugin_version", "distrib_version"))
        parser_addon_mgr.add_argument("distribType", action='store_const', const=self.distrib_type,
                                      help=argparse.SUPPRESS)
        parser_addon_mgr.set_defaults(func=PluginCmd.pluginmgr)

        if self.distrib_type != "community":
            parser_addon_pkgr = main_sub_parsers.add_parser(name="pluginpkgr",
                                                            description="Package a supported Ariane plugin",
                                                            help="[-h] user name version distrib_version")
        else:
            parser_addon_pkgr = main_sub_parsers.add_parser(name="pluginpkgr",
                                                            description="Package a supported Ariane plugin",
                                                            help="[-h] name version distrib_version")

        if self.distrib_type != "community":
            parser_addon_pkgr.add_argument("user", help="Stash username")

        parser_addon_pkgr.add_argument("name", help="Ariane plugin name to package")
        parser_addon_pkgr.add_argument("version", help="Ariane plugin version to package")
        parser_addon_pkgr.add_argument("dversion", help="Ariane distrib version base")
        parser_addon_pkgr.add_argument("distribType", action='store_const', const=self.distrib_type,
                                       help=argparse.SUPPRESS)
        parser_addon_pkgr.set_defaults(func=PluginCmd.pluginpkgr)

        parser_distribution_mgr = main_sub_parsers.add_parser(name="distmgr",
                                                              description="Manage supported Ariane distributions "
                                                                          "version",
                                                              help="[-h] (-d distribution_version "
                                                                   "[distribution_deployment_type] | -l)")
        me_group_distribution_mgr = parser_distribution_mgr.add_mutually_exclusive_group(required=True)
        # meGroupDistributionMgr.add_argument("-a", "--add", help="Add a supported distribution version", nargs=1)
        me_group_distribution_mgr.add_argument("-d", "--details", help="Show supported distribution details", nargs='+')
        me_group_distribution_mgr.add_argument("-l", "--list", help="List supported distribution version",
                                               action="store_true")
        # meGroupDistributionMgr.add_argument("-r", "--remove", help="Remove a supported distribution version", nargs=1)
        parser_distribution_mgr.add_argument("distribType", action='store_const', const=self.distrib_type,
                                             help=argparse.SUPPRESS)
        parser_distribution_mgr.set_defaults(func=DistribCmd.distmgr)

        if self.distrib_type != "community":
            parser_distribution_pkgr = main_sub_parsers.add_parser(name="distpkgr",
                                                                   description="Package a distribution",
                                                                   help="[-h] user version")
        else:
            parser_distribution_pkgr = main_sub_parsers.add_parser(name="distpkgr",
                                                                   description="Package a distribution",
                                                                   help="[-h] version")
        if self.distrib_type != "community":
            parser_distribution_pkgr.add_argument("user", help="Stash username")
        parser_distribution_pkgr.add_argument("version", help="Ariane distribution version to package")
        parser_distribution_pkgr.add_argument("distribType", action='store_const', const=self.distrib_type,
                                              help=argparse.SUPPRESS)
        parser_distribution_pkgr.set_defaults(func=DistribCmd.dispkgr)

        if self.distrib_type != "community":
            parser_add_git_repo = main_sub_parsers.add_parser(name="gitadd", description="Add a new Ariane git"
                                                                                         " repository",
                                                              help="[-h] name url {plugin,core}")
            parser_add_git_repo.add_argument("name", help="Ariane git repository name")
            parser_add_git_repo.add_argument("url", help="Ariane git repository url")
            parser_add_git_repo.add_argument("type", help="Specifiy if target git repository is a Ariane core component"
                                                          " or a Ariane plugin", choices=["plugin", "core"])
            parser_add_git_repo.set_defaults(func=GitCmd.git_add)

            parser_git_branch = main_sub_parsers.add_parser(name="gitbranch", description="List existing branch of "
                                                                                          "a git repository",
                                                            help="[-h] user name")
            parser_git_branch.add_argument("user", help="Stash username")
            parser_git_branch.add_argument("name", help="Ariane git repository name")
            parser_git_branch.set_defaults(func=GitCmd.git_branch)

            parser_list_git_repo = main_sub_parsers.add_parser(name="gitlist",
                                                               description="List Ariane git repositories",
                                                               help="[-h] [-a | -c]")
            me_group_list_git_repo = parser_list_git_repo.add_mutually_exclusive_group()
            me_group_list_git_repo.add_argument("-a", "--plugin", help="list Ariane plugin repositories only",
                                                action="store_true")
            me_group_list_git_repo.add_argument("-c", "--core", help="list Ariane core repositories only",
                                                action="store_true")
            parser_list_git_repo.set_defaults(func=GitCmd.git_list)

            parser_remove_git_repo = main_sub_parsers.add_parser(name="gitremove",
                                                                 description="Remove a Ariane git repository",
                                                                 help="[-h] name")
            parser_remove_git_repo.add_argument("name", help="Ariane git repository name to remove")
            parser_remove_git_repo.set_defaults(func=GitCmd.git_remove)

            parser_git_tag = main_sub_parsers.add_parser(name="gittag", description="List existing tag of a git "
                                                                                    "repository",
                                                         help="[-h] user name")
            parser_git_tag.add_argument("user", help="Stash username")
            parser_git_tag.add_argument("name", help="Ariane git repository name")
            parser_git_tag.set_defaults(func=GitCmd.git_tag)

        return parser.parse_args()
