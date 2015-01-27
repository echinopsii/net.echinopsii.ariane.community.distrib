# packager sources manager
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
import json
import os
import shutil
from subprocess import call
import tempfile
from tools.DistributionRegistry import DistributionRegistry

__author__ = 'mffrench'


class SourcesManager:

    def __init__(self, gitTarget, distribType, version):
        self.gitTarget = gitTarget
        self.version = version
        self.distribType = distribType
        self.gitRepos = json.load(open("resources/sources/ariane." + self.distribType + ".git.repos-" + self.version + ".json"))

        if self.version != "master.SNAPSHOT":
            if os.path.exists(self.gitTarget):
                shutil.rmtree(self.gitTarget)
        else:
            print("Ariane integration manager is working on your DEV environment")

    @staticmethod
    def cloneOrUpdate(target, version, repoURL):
        if not os.path.exists(target):
            os.makedirs(target)
            ret = call(["git", "clone", repoURL, target])
            if ret != 0:
                raise RuntimeError("Repository clone failed")
            if version != "master.SNAPSHOT":
                pwd = os.getcwd()
                os.chdir(target)
                ret = call(["git", "checkout", version])
                os.chdir(pwd)
                if ret != 0:
                    raise RuntimeError("Repository checkout failed")

        elif version == "master.SNAPSHOT":
            pwd = os.getcwd()
            os.chdir(target)
            ret = call(["git", "pull"])
            if ret != 0:
                raise RuntimeError("Repository pull failed")
            os.chdir(pwd)

    def cloneCore(self, user, password):
        distribution = DistributionRegistry(self.distribType).getDistribution(self.version)
        if distribution is not None:
            distributionDetails = distribution.details()

            for module in self.gitRepos.keys():
                gitRepo = self.gitRepos[module]
                if self.distribType != "community":
                    gitRepoURL = gitRepo["url"].split('://')[0] + "://" + user + ":" + password + "@" + gitRepo["url"].split("https://")[1]
                else:
                    gitRepoURL = gitRepo["url"]
                gitRepoType = gitRepo["type"]

                if gitRepoType == "core" or gitRepoType == "environment":
                    moduleTarget = self.gitTarget + "/" + module
                    moduleVersion = distributionDetails[module]
                    SourcesManager.cloneOrUpdate(moduleTarget, moduleVersion, gitRepoURL)

        else:
            raise ValueError("Provided distribution version " + self.version + "is not valid")

        return self

    def clonePlugin(self, user, password, pluginName, pluginVersion):
        gitPlugin = self.gitRepos.get(pluginName)
        if gitPlugin is not None:
            if self.distribType != "community":
                gitRepoURL = gitPlugin["url"].split('://')[0] + "://" + user + ":" + password + "@" + gitPlugin["url"].split("https://")[1]
            else:
                gitRepoURL = gitPlugin["url"]
            if self.version != "master.SNAPSHOT":
                pluginTarget = self.gitTarget + "/" + pluginName + "-" + pluginVersion
            else:
                pluginTarget = self.gitTarget + "/" + pluginName
            SourcesManager.cloneOrUpdate(pluginTarget, pluginVersion, gitRepoURL)

        else:
            raise ValueError("Provided plugin " + pluginName + " is not valid.")

        return self

    def compileCore(self):
        distribution = DistributionRegistry(self.distribType).getDistribution(self.version)
        if distribution is not None:
            shutil.copy(distribution.mavenFile, self.gitTarget + "/pom.xml")
            pwd = os.getcwd()
            os.chdir(self.gitTarget)
            call(["mvn", "clean", "install", "-Dmaven.test.skip=true"])
            os.chdir(pwd)

        else:
            raise RuntimeError("Provided distribution version " + self.version + " is not valid")

        return self

    def compilePlugin(self, addonName, pluginVersion):
        if self.version != "master.SNAPSHOT":
            pluginTarget = self.gitTarget + "/" + addonName + "-" + pluginVersion
        else:
            pluginTarget = self.gitTarget + "/" + addonName
        if os.path.exists(pluginTarget):
            pwd = os.getcwd()
            os.chdir(pluginTarget)
            call(["mvn", "clean", "install", "-Dmaven.test.skip=true"])
            os.chdir(pwd)

        else:
            raise RuntimeError("Unable to find plugin source folder " + pluginTarget + ". Has the git repo been cloned ?")

        return self
