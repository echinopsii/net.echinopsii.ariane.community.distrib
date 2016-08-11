# CC git repositories manager
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
import getpass
import json
import requests

__author__ = 'mffrench'


class GitCmd:

    @staticmethod
    def stash_rest(url, user, pwd):
        r = requests.get(url, auth=(user, pwd))
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            print("Authentication error")
            return None
        else:
            print("Error. Status code: " + str(r.status_code))
            return None

    @staticmethod
    def git_add(args, script_path):
        current = OrderedDict(sorted(json.load(
            open(script_path+"/resources/sources/ariane.community.git.repos-SNAPSHOT.json")).items(),
            key=lambda t: t[0]))
        dicto = dict()
        for key in current.keys():
            dicto[key] = current[key]
        dicto[args.name] = {"url": args.url, "type": args.type}

        git_repos_json = open(script_path+"/resources/sources/ariane.community.git.repos-SNAPSHOT.json", "w")
        json_str = json.dumps(dicto, sort_keys=True, indent=4, separators=(',', ': '))
        git_repos_json.write(json_str)
        git_repos_json.close()

    @staticmethod
    def git_branch(args, script_path):
        password = getpass.getpass("Stash password : ")
        json_branches = GitCmd.stash_rest('http://stash.lab.prod.dekatonshivr.echinopsii.net:7990/'
                                          'rest/api/1.0/projects/ariane/repos/' + args.name + '/branches',
                                          args.user, password)
        if json_branches is not None:
            print("\nExisting branchs of git repository " + args.name + " :\n")
            for value in json_branches["values"]:
                print(value["displayId"])

    @staticmethod
    def git_list(args, script_path):
        ariane_git_repos = OrderedDict(sorted(json.load(
            open(script_path+"/resources/sources/ariane.community.git.repos-SNAPSHOT.json")).items(),
            key=lambda t: t[0]))
        if args.addon:
            print("\nExisting Ariane addon git repositories :\n")
            print('{:40} {:110}'.format("Ariane git repository name", "Ariane git repository URL"))
            print('{:40} {:110}'.format("--------------------------", "-------------------------"))
            for key in ariane_git_repos.keys():
                git_repo = ariane_git_repos[key]
                if git_repo['type'] == "addon":
                    print('{:40} {:110}'.format(key, git_repo['url']))
        elif args.core:
            print("\nExisting Ariane core git repositories :\n")
            print('{:40} {:110}'.format("Ariane git repository name", "Ariane git repository URL"))
            print('{:40} {:110}'.format("--------------------------", "-------------------------"))
            for key in ariane_git_repos.keys():
                git_repo = ariane_git_repos[key]
                if git_repo['type'] == "core":
                    print('{:40} {:110}'.format(key, git_repo['url']))
        else:
            print("\nExisting Ariane git repositories :\n")
            print('{:40} {:110} {:25}'.format("Ariane git repository name", "Ariane git repository URL",
                                              "Ariane git repository type"))
            print('{:40} {:110} {:25}'.format("--------------------------", "-------------------------",
                                              "--------------------------"))
            for key in ariane_git_repos.keys():
                git_repo = ariane_git_repos[key]
                print('{:40} {:110} {:25}'.format(key, git_repo['url'], git_repo['type']))

    @staticmethod
    def git_remove(args, script_path):
        ariane_git_repos = OrderedDict(sorted(json.load(
            open(script_path+"/resources/sources/ariane.community.git.repos-SNAPSHOT.json")).items(),
            key=lambda t: t[0]))
        for key in ariane_git_repos.keys():
            if args.name == key:
                ariane_git_repos.pop(key)

        git_repos_json = open(script_path+"/resources/sources/ariane.community.git.repos-SNAPSHOT.json", "w")
        json_str = json.dumps(ariane_git_repos, sort_keys=True, indent=4, separators=(',', ': '))
        git_repos_json.write(json_str)
        git_repos_json.close()

    @staticmethod
    def git_tag(args, script_path):
        password = getpass.getpass("Stash password : ")
        json_tags = GitCmd.stash_rest(
            'http://stash.lab.prod.dekatonshivr.echinopsii.net:7990/rest/api/1.0/projects/ariane/repos/' + args.name +
            '/tags', args.user, password)
        if json_tags is not None:
            print("\nExisting tags of git repository " + args.name + " :\n")
            for value in json_tags["values"]:
                print(value["displayId"])
