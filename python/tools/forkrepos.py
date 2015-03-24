#!/usr/bin/python3
#
# Ariane community distrib main
#
# Copyright (C) 2015 Sagar Ghuge
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
import time
import getpass
import os

__author__ = 'gsagar'

class ForkRepo:

    def __init__(self):
        self.scheme = None
        self.netloc = None
        self.path = None
        self.URL = None
        self.githubAPIUrl = "https://api.github.com/"
        self.stashAPIUrl = "https://stash.echinopsii.net/rest/api/1.0/projects/ARIANE/"
        self.cloneRef = "../resources/sources/ariane.community.git.repos-master.SNAPSHOT.json"
        self.forkRef = "../resources/sources/ariane.community.git.fork-repos-master.SNAPSHOT.json"
        self.user = self.password = None
        self.readConfig()

    def fork_callback(r, *args, **kwargs):
        print("Forking repo : %s"%(args))

    def gitIsRemoteFork(self, repo_name, urltype):
        if "github" in urltype:
            reqResult = requests.get(urltype+ "repos/" + repo_name)
            requestJSONObj = json.loads(reqResult.text)
            return ("parent" in requestJSONObj)
        elif "stash" in urltype:
            # https://stash.echinopsii.net/rest/api/1.0/projects/ARIANE/repos/ariane.community.installer/forks
            reqResult = requests.get(urltype+ "repos/" +repo_name+ "/forks", auth=(self.user, self.password), verify=False)
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
                    stash_repo_name = val["url"].strip("net.echinopsii")
                    if self.user:
                        if "github" in self.netloc:
                            val["url"] = self.scheme +"://"+ self.netloc +"/"+ self.user +"/"+ val["url"] + ".git"
                        else:
                            val["url"] = self.scheme +"://"+ self.netloc +"/scm/~"+ self.user +"/"+ stash_repo_name + ".git"
                    else:
                        if "github" in self.netloc:
                            val["url"] = self.scheme +"://"+ self.netloc +"/echinopsii/"+ val["url"] + ".git"
                        else:
                            val["url"] = self.scheme +"://"+ self.netloc +"/scm/ariane/"+ stash_repo_name + ".git"

                clonefp.write(json.dumps(self.gitForkRepoData))
                print("\nClone reference file genrated...\n")

        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def setCredentials(self):
      #TODO validate credentials
      if not (self.user and self.password):
            print("*_* Tool will fork other repos for you *_* \n")
            self.user= input("User Name: ")
            self.password=getpass.getpass()

    def gitFork(self, path):
        remotepath = "/"+self.user+"/"+path
        if self.gitIsRemoteFork(remotepath, self.githubAPIUrl):
            reqResult = requests.post(
                self.githubAPIUrl+ "repos"+path+"/forks",
                hooks=dict(response=self.fork_callback(path)),
                auth=(self.user, self.password), timeout=300)

            forkHook = requests.post(
                self.githubAPIUrl+"repos"+path+"/hooks",
                params={"events":["fork"]})

            if (reqResult.status_code == 202):
                print("Accepted for forking")
            else:
                print("Failed")
        else:
            print("Repository : %s already forked"%(remotepath))
    

    def setForkRefData(self):
        try:
            with open(self.forkRef) as fp:
                self.gitForkRepoData = json.loads(fp.read())
            fp.close()
        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def gitForkRepos(self):
        for key, val in self.gitForkRepoData.items():
            parseResult = urlparse(val["url"])
            self.gitFork(parseResult.path)

        self.generateCloneRef()

    def stashForkRepos(self):
        # Check for if repos are forked or not
        # and depend on that fork relevant repo and
        # generate clone Ref
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
                self.gitForkRepos()
            else:
                # start with echinopsii then it's cloned only
                # generate the ref depend on it
                self.generateCloneRef()

        elif "stash" in self.netloc:
            #http://sagarghuge@stash.echinopsii.net/scm/~sagarghuge/ariane.community.distrib.git
            #http://stash.echinopsii.net/scm/ariane/ariane.community.distrib.git
            if self.isForked(self.netloc, self.stashAPIUrl):
                self.setCredentials()
                self.stashForkRepos()
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
