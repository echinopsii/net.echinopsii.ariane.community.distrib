#!/usr/bin/python3
#
# Ariane community distrib main
#
# Copyright (C) 2015 Sagar Ghuge <ghugesss@gmail.com>
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
from urllib.parse import urlparse
import re
import requests
import json
import getpass

__author__ = 'gsagar'

class ForkRepo:

    def __init__(self):
        self.scheme = None
        self.netloc = None
        self.path = None
        self.URL = None
        self.githubAPIUrl = "https://api.github.com/"
        self.stashAPIUrl = "https://stash.echinopsii.net/rest/api/1.0/"
        self.cloneRef = "../resources/sources/ariane.community.git.repos-master.SNAPSHOT.json"
        self.forkRef = "../resources/sources/ariane.community.git.fork-repos-master.SNAPSHOT.json"
        self.user = self.password = None
        self.readConfig()

    def fork_callback(r, *args, **kwargs):
        print("Forking repository : %s"%(args))

    def isRemoteFork(self, repo_name, urltype):
        if "github" in urltype:
            reqResult = requests.get(urltype + "repos" + repo_name)
            requestJSONObj = json.loads(reqResult.text)
            if "parent" in requestJSONObj:
                return True
            return False
        elif "stash" in urltype:
            reqResult = requests.get(
                urltype + "projects/ARIANE/repos/" + repo_name + "/forks",
                auth=(self.user, self.password), verify=False)
            requestJSONObj = json.loads(reqResult.text)
            if requestJSONObj["values"] == []:
                return False
            return True

    def isForked(self, path, urltype):
        if "github" in urltype:
            return path.startswith("/echinopsii")
        elif "stash" in urltype:
            return ("@" in path)

    def generateCloneRef(self):
        try:
            with open(self.cloneRef, "w") as clonefp:
                for key, val in self.gitForkRepoData.items():
                    stash_repo_name = val["url"].split("net.echinopsii.")[1]
                    if self.user:
                        if "github" in self.netloc:
                            val["url"] = self.scheme + "://" + self.netloc + "/" + self.user + "/" + val["url"] + ".git"
                        else:
                            val["url"] = self.scheme + "://" + self.netloc + "/scm/~" + self.user + "/" + stash_repo_name + ".git"
                    else:
                        if "github" in self.netloc:
                            val["url"] = self.scheme + "://" + self.netloc + "/echinopsii/" + val["url"] + ".git"
                        else:
                            val["url"] = self.scheme + "://" + self.netloc + "/scm/ariane/" + stash_repo_name + ".git"

                clonefp.write(json.dumps(self.gitForkRepoData, indent=4, separators=(',', ': ')))
                print("\nClone reference file genrated...\n")

        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def validateCredentials(self):
        attempt = 1
        while attempt >= 0:
            if "github" in self.netloc:
                requestObj = requests.get(self.githubAPIUrl + 'user', auth=(self.user, self.password))
            else:
                requestObj = requests.get(self.stashAPIUrl + "users", auth=(self.user, self.password), verify=False)

            if requestObj.status_code == 200:
                return True
            else:
                print("Sorry, try again")
                self.password = getpass.getpass()
            attempt = attempt -1
        return False

    def setCredentials(self):
      if not (self.user and self.password):
            print("*_* Tool will fork other repos for you *_* \n")
            self.user = input("User Name: ")
            self.password = getpass.getpass()
            if not self.validateCredentials():
                exit(0)

    def gitFork(self, path):
        remotepath = "/" + self.user + "/" + path
        if not self.isRemoteFork(remotepath, self.githubAPIUrl):
            reqResult = requests.post(
                self.githubAPIUrl+ "repos/echinopsii/" + path + "/forks",
                hooks=dict(response=self.fork_callback(path)),
                auth=(self.user, self.password), timeout=300)

            forkHook = requests.post(
                self.githubAPIUrl + "repos" + path + "/hooks",
                params={"events":["fork"]})

            if (reqResult.status_code == 202):
                print("Accepted for forking")
            else:
                print("Failed")
        else:
            print("Repository : %s already forked" %(remotepath))

    def stashFork(self, path):
        if not self.isRemoteFork(path, self.stashAPIUrl):
            reqResult = requests.post(
                self.stashAPIUrl + "projects/ARIANE/repos/" + path,
                headers={"Content-Type" : "application/json"},
                verify=False, auth=(self.user, self.password), data='{}')

            if (reqResult.status_code == 201):
                print("Forking repository : %s"%(path))
        else:
            print("Repository : %s already forked" %(path))

    def setForkRefData(self):
        try:
            with open(self.forkRef) as fp:
                self.gitForkRepoData = json.loads(fp.read())
            fp.close()
        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def forkRepos(self):
        self.setCredentials()
        for key, val in self.gitForkRepoData.items():
            parseResult = urlparse(val["url"])

            if "github" in self.netloc:
                self.gitFork(parseResult.path)
            else:
                self.stashFork(parseResult.path.split("net.echinopsii.")[1])

        self.generateCloneRef()

    def setVars(self):
        parseResult = urlparse(self.URL)
        self.scheme = parseResult.scheme
        self.netloc = parseResult.netloc
        self.path = parseResult.path[:-4]

        self.setForkRefData()
        if "github" in self.netloc:
            #https://github.com/echinopsii/net.echinopsii.ariane.community.distrib.git
            #https://github.com/sagarghuge/net.echinopsii.ariane.community.distrib.git
            if not self.isForked(self.path, self.githubAPIUrl):
                self.forkRepos()
            else:
                # start with echinopsii then it's cloned only
                # generate the ref depend on it
                self.generateCloneRef()

        elif "stash" in self.netloc:
            #http://user@stash.echinopsii.net/scm/~user/ariane.community.distrib.git
            #http://stash.echinopsii.net/scm/ariane/ariane.community.distrib.git
            if self.isForked(self.netloc, self.stashAPIUrl):
                self.forkRepos()
            else:
                self.generateCloneRef()

    def readConfig(self):
        try:
            with open("../../.git/config") as gitconfigObj:
                for line in gitconfigObj.readlines():
                    if re.match("\turl", line):
                        self.URL = line.split("=")[1].strip()
                        break
        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

        if (self.URL):
            self.setVars()
        else:
            raise Exception("Can't find any URL")

if __name__ == "__main__":

    fork = ForkRepo()
