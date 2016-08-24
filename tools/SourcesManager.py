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
import subprocess
from tools.DistributionRegistry import DistributionRegistry

__author__ = 'mffrench'


class SourcesManager:

    def __init__(self, git_target, distrib_type, version, script_path, distrib_dep_type="mno"):
        self.git_target = git_target
        self.version = version
        self.distrib_type = distrib_type
        self.distrib_dep_type = distrib_dep_type
        self.script_path = script_path
        if '.SNAPSHOT' in self.version:
            self.distrib_version = self.version.split('.SNAPSHOT')[0]
        else:
            self.distrib_version = self.version

        self.git_repos = \
            json.load(open(self.script_path + "/resources/sources/ariane." + self.distrib_type +
                           ".git.repos-" + self.distrib_version + ".json"))

        if 'SNAPSHOT' not in self.version:
            if os.path.exists(self.git_target):
                shutil.rmtree(self.git_target)
        else:
            print("Ariane integration manager is working on your DEV environment")

    @staticmethod
    def is_git_tagged(version, path=None):
        tag_flag = False
        tags = []
        if path is not None:
            if os.path.exists(path):
                tags = subprocess.check_output("git tag", shell=True, cwd=path)
        else:
            tags = subprocess.check_output("git tag", shell=True)
        # check_output gives the command output in bytes format, so we decode it.
        if (isinstance(tags, bytes)) and (len(tags) > 0):
            tags = (tags.decode()).split('\n')
            if tags[-1] == '':
                tags = tags[:-1]
            for tag in tags:
                if tag == version:
                    tag_flag = True
                    break
        return tag_flag

    @staticmethod
    def clone_or_update(target, version, repo_url, branch=None):
        if not os.path.exists(target):
            os.makedirs(target)
            ret = call(["git", "clone", repo_url, target])
            if ret != 0:
                raise RuntimeError("Repository clone failed")
            if 'SNAPSHOT' not in version:
                pwd = os.getcwd()
                os.chdir(target)
                ret = call(["git", "checkout", version])
                os.chdir(pwd)
                if ret != 0:
                    raise RuntimeError("Repository checkout failed")

        elif branch is not None:
            pwd = os.getcwd()
            os.chdir(target)
            # call(["git", "remote", "set-url", "origin", repo_url])
            ret = call(["git", "pull"])
            if ret != 0:
                raise RuntimeError("Repository pull failed")
            ret = call(["git", "checkout", branch])
            if ret != 0:
                raise RuntimeError("Repository checkout failed (" + branch + ")")
            os.chdir(pwd)

        else:
            pwd = os.getcwd()
            os.chdir(target)
            if 'SNAPSHOT' not in version:
                pwd = os.getcwd()
                os.chdir(target)
                ret = call(["git", "checkout", version])
                os.chdir(pwd)
                if ret != 0:
                    raise RuntimeError("Repository checkout failed")

    def reinit_dev_repos(self, user, password):
        if 'SNAPSHOT' in self.version:
            distribution = DistributionRegistry(self.distrib_type, self.script_path).get_distribution(
                self.distrib_version, self.distrib_dep_type
            )
            if distribution is not None:
                distribution_details = distribution.details()
                build_distributions_details = distribution.build_details()

                for module in self.git_repos.keys():
                    if module in distribution_details:
                        git_repo = self.git_repos[module]
                        if self.distrib_type != "community":
                            git_repo_url = git_repo["url"].split('://')[0] + "://" + user + ":" + password + "@" + \
                                           git_repo["url"].split("https://")[1]
                        else:
                            git_repo_url = git_repo["url"]
                        git_repo_type = git_repo["type"]

                        if git_repo_type == "core" or git_repo_type == "environment" or git_repo_type == "library":
                            module_target = self.git_target + "/" + module
                            module_version = distribution_details[module]
                            module_branch = build_distributions_details[module].split(".")[0]
                            SourcesManager.clone_or_update(module_target, module_version,
                                                           git_repo_url, branch=module_branch)
        return self

    def clone_core(self, user, password):
        distribution = DistributionRegistry(self.distrib_type, self.script_path).get_distribution(
            self.distrib_version, self.distrib_dep_type
        )
        if distribution is not None:
            distribution_details = distribution.details()
            build_distributions_details = distribution.build_details()

            for module in self.git_repos.keys():
                if module in distribution_details:
                    git_repo = self.git_repos[module]
                    if self.distrib_type != "community":
                        git_repo_url = git_repo["url"].split('://')[0] + "://" + user + ":" + password + "@" + \
                            git_repo["url"].split("https://")[1]
                    else:
                        git_repo_url = git_repo["url"]
                    git_repo_type = git_repo["type"]

                    if git_repo_type == "core" or git_repo_type == "environment" or git_repo_type == "library":
                        module_target = self.git_target + "/" + module
                        module_version = distribution_details[module]
                        if "SNAPSHOT" in self.version:
                            if SourcesManager.is_git_tagged(module_version, module_target):
                                module_branch = None
                            else:
                                module_branch = build_distributions_details[module].split(".")[0]
                        else:
                            module_branch = None

                        SourcesManager.clone_or_update(module_target, module_version,
                                                       git_repo_url, branch=module_branch)

        else:
            raise ValueError("Provided distribution version " + self.version + " is not valid")

        return self

    def clone_plugin(self, user, password, plugin_name, plugin_version):
        git_plugin = self.git_repos.get(plugin_name)
        if git_plugin is not None:
            if self.distrib_type != "community":
                git_repo_url = git_plugin["url"].split('://')[0] + "://" + user + ":" + password + "@" + \
                    git_plugin["url"].split("https://")[1]
            else:
                git_repo_url = git_plugin["url"]

            if 'SNAPSHOT' not in self.version:
                plugin_target = self.git_target + "/" + plugin_name + "-" + plugin_version
            else:
                plugin_target = self.git_target + "/" + plugin_name
            SourcesManager.clone_or_update(plugin_target, plugin_version, git_repo_url)

        else:
            raise ValueError("Provided plugin " + plugin_name + " is not valid.")

        return self

    def compile_core(self):
        distribution = DistributionRegistry(self.distrib_type, self.script_path).get_distribution(
            self.distrib_version, self.distrib_dep_type
        )
        if distribution is not None:
            shutil.copy(distribution.maven_file, self.git_target + "/pom.xml")
            pwd = os.getcwd()
            os.chdir(self.git_target)
            exitcode = call(["mvn", "clean", "install", "-Dmaven.test.skip=true"])
            os.chdir(pwd)

            if exitcode:
                raise RuntimeError("Compilation did not work for version: {0}, distribution: {1}".
                                   format(self.version, self.distrib_type))

        else:
            raise RuntimeError("Provided distribution version " + self.version + " is not valid")

        return self

    def compile_plugin(self, addon_name, plugin_version):
        if 'SNAPSHOT' not in self.version:
            plugin_target = self.git_target + "/" + addon_name + "-" + plugin_version
        else:
            plugin_target = self.git_target + "/" + addon_name
        if os.path.exists(plugin_target):
            if os.path.exists(plugin_target+"/pom.xml"):
                pwd = os.getcwd()
                os.chdir(plugin_target)
                exitcode = call(["mvn", "clean", "install", "-Dmaven.test.skip=true"])
                os.chdir(pwd)
                if exitcode:
                    raise RuntimeError("Compilation did not work for addon: {0} version: {1}".
                                       format(addon_name, plugin_version))

        else:
            raise RuntimeError("Unable to find plugin source folder " + plugin_target +
                               ". Has the git repo been cloned ?")

        return self
