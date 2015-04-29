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
    def stashRest(url, user, pwd):
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
    def gitAdd(args,scriptPath):
        current = OrderedDict(sorted(json.load(open(scriptPath+"/resources/sources/ariane.community.git.repos-master.SNAPSHOT.json")).items(), key=lambda t: t[0]))
        dicto = dict()
        for key in current.keys():
            dicto[key] = current[key]
        dicto[args.name] = {"url": args.url, "type": args.type}

        gitReposJSON = open(scriptPath+"/resources/sources/ariane.community.git.repos-master.SNAPSHOT.json", "w")
        jsonStr = json.dumps(dicto, sort_keys=True, indent=4, separators=(',', ': '))
        gitReposJSON.write(jsonStr)
        gitReposJSON.close()

    @staticmethod
    def gitBranch(args,scriptPath):
        password = getpass.getpass("Stash password : ")
        json = GitCmd.stashRest('http://stash.lab.prod.dekatonshivr.echinopsii.net:7990/rest/api/1.0/projects/ariane/repos/' + args.name + '/branches', args.user, password)
        if json is not None:
            print("\nExisting branchs of git repository " + args.name + " :\n")
            for value in json["values"]:
                print(value["displayId"])

    @staticmethod
    def gitList(args,scriptPath):
        ccGitRepos = OrderedDict(sorted(json.load(open(scriptPath+"/resources/sources/ariane.community.git.repos-master.SNAPSHOT.json")).items(), key=lambda t: t[0]))
        if args.addon:
            print("\nExisting Ariane addon git repositories :\n")
            print('{:40} {:110}'.format("Ariane git repository name", "Ariane git repository URL"))
            print('{:40} {:110}'.format("--------------------------", "-------------------------"))
            for key in ccGitRepos.keys():
                gitRepo = ccGitRepos[key]
                if gitRepo['type'] == "addon":
                    print('{:40} {:110}'.format(key, gitRepo['url']))
        elif args.core:
            print("\nExisting Ariane core git repositories :\n")
            print('{:40} {:110}'.format("Ariane git repository name", "Ariane git repository URL"))
            print('{:40} {:110}'.format("--------------------------", "-------------------------"))
            for key in ccGitRepos.keys():
                gitRepo = ccGitRepos[key]
                if gitRepo['type'] == "core":
                    print('{:40} {:110}'.format(key, gitRepo['url']))
        else:
            print("\nExisting Ariane git repositories :\n")
            print('{:40} {:110} {:25}'.format("Ariane git repository name", "Ariane git repository URL", "Ariane git repository type"))
            print('{:40} {:110} {:25}'.format("--------------------------", "-------------------------", "--------------------------"))
            for key in ccGitRepos.keys():
                gitRepo = ccGitRepos[key]
                print('{:40} {:110} {:25}'.format(key, gitRepo['url'], gitRepo['type']))

    @staticmethod
    def gitRemove(args,scriptPath):
        ccGitRepos = OrderedDict(sorted(json.load(open(scriptPath+"/resources/sources/ariane.community.git.repos-master.SNAPSHOT.json")).items(), key=lambda t: t[0]))
        for key in ccGitRepos.keys():
            if args.name == key:
                ccGitRepos.pop(key)

        gitReposJSON = open(scriptPath+"/resources/sources/ariane.community.git.repos-master.SNAPSHOT.json", "w")
        jsonStr = json.dumps(ccGitRepos, sort_keys=True, indent=4, separators=(',', ': '))
        gitReposJSON.write(jsonStr)
        gitReposJSON.close()

    @staticmethod
    def gitTag(args,scriptPath):
        password = getpass.getpass("Stash password : ")
        json = GitCmd.stashRest('http://stash.lab.prod.dekatonshivr.echinopsii.net:7990/rest/api/1.0/projects/ariane/repos/' + args.name + '/tags', args.user, password)
        if json is not None:
            print("\nExisting tags of git repository " + args.name + " :\n")
            for value in json["values"]:
                print(value["displayId"])
