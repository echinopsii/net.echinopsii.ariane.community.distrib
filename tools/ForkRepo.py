#!/usr/bin/python3
#
# Ariane community distrib main
#
# Copyright(C) 2015 echinopsii
# Author : Sagar Ghuge ghugess@gmail.com
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
import configparser
from urllib.parse import urlparse
import re
import requests
import json
import getpass
import os

__author__ = 'gsagar'


class ForkRepo:

    def __init__(self, distrib_type, script_path):
        # Get full path of script and remove script name as well as tools directory
        self.script_path = script_path

        self.scheme = None
        self.netloc = None
        self.path = None
        self.URL = None
        self.github_api_url = "https://api.github.com/"
        self.stash_api_url = "https://stash.echinopsii.net/rest/api/1.0/"
        self.clone_ref = self.script_path + "/resources/sources/ariane." + distrib_type + \
                         ".git.repos-master.SNAPSHOT.json"
        self.main_ref = self.script_path + "/resources/sources/ariane." + distrib_type + \
                        ".git.repos-main-master.SNAPSHOT.json"
        self.user = self.password = None
        self.git_fork_repo_data = None

    @staticmethod
    def fork_callback(*args):
        print("Forking repository : %s" % args)

    def is_remote_fork(self, repo_name, urltype):
        if "github" in urltype:
            req_result = requests.get(urltype + "repos" + repo_name)
            request_json_obj = json.loads(req_result.text)
            if "parent" in request_json_obj:
                return True
            return False
        elif "stash" in urltype:
            req_result = requests.get(
                urltype + "users/" + self.user + "/repos/" + repo_name,
                auth=(self.user, self.password), verify=False)
            request_json_obj = json.loads(req_result.text)
            if "errors" in request_json_obj:
                if request_json_obj["errors"][0]["exceptionName"] == \
                        "com.atlassian.stash.exception.NoSuchRepositoryException":
                    return False
            return True

    @staticmethod
    def is_cloned(path, url_type):
        if "github" in url_type:
            return path.startswith("/echinopsii")
        elif "stash" in url_type:
            return "/scm/ariane/" in path or "/scm/arianep/" in path

    def generate_clone_ref(self, is_cloned):
        try:
            with open(self.clone_ref, "w") as clone_fp:
                for key, val in self.git_fork_repo_data.items():
                    stash_repo_name = val["url"].split("net.echinopsii.")[1]
                    is_enterprise = 'enterprise' in stash_repo_name
                    if is_enterprise:
                        project_code = 'arianep'
                    else:
                        project_code = 'ariane'

                    if not is_cloned:
                        if "github" in self.netloc:
                            val["url"] = self.scheme + "://" + self.netloc + "/" + self.user + "/" + val["url"] + ".git"
                        else:
                            val["url"] = self.scheme + "://" + self.netloc + "/scm/~" + self.user + "/" + \
                                         stash_repo_name + ".git"
                    else:
                        if "github" in self.netloc:
                            val["url"] = self.scheme + "://" + self.netloc + "/echinopsii/" + val["url"] + ".git"
                        else:
                            val["url"] = self.scheme + "://" + self.netloc +  '/scm/' + project_code + '/' + \
                                         stash_repo_name + ".git"

                clone_fp.write(json.dumps(self.git_fork_repo_data, indent=4, separators=(',', ': ')))
                print("\nClone reference file genrated...\n")

        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def validate_credentials(self):
        attempt = 1
        while attempt >= 0:
            if "github" in self.netloc:
                request_obj = requests.get(self.github_api_url + 'user', auth=(self.user, self.password))
            else:
                request_obj = requests.get(self.stash_api_url + "users", auth=(self.user, self.password), verify=False)

            if request_obj.status_code == 200:
                return True
            else:
                print("Sorry, try again")
                self.password = getpass.getpass()
            attempt -= 1
        return False

    def set_credentials(self):
        if not self.user or not self.password:
            if os.path.isfile(self.script_path + "/.gitauth"):
                config = configparser.ConfigParser()
                config.read(self.script_path + "/.gitauth")
                self.user = config['GITAUTH']['user'] if config['GITAUTH'] else None
                self.password = config['GITAUTH']['password'] if config['GITAUTH'] else None

            if not self.user or not self.password:
                self.user = input("User Name: ")
                self.password = getpass.getpass()
                if not self.validate_credentials():
                    exit(0)
                else:
                    config = configparser.ConfigParser()
                    config["GITAUTH"] = {
                        'user': self.user,
                        'password': self.password
                    }
                    with open(self.script_path + "/.gitauth", 'w') as configfile:
                        config.write(configfile)
                    pass

    def git_fork(self, path):
        remote_path = "/" + self.user + "/" + path
        if not self.is_remote_fork(remote_path, self.github_api_url):
            req_result = requests.post(
                self.github_api_url + "repos/echinopsii/" + path + "/forks",
                hooks=dict(response=self.fork_callback(path)),
                auth=(self.user, self.password), timeout=300)

            requests.post(
                self.github_api_url + "repos" + path + "/hooks",
                params={"events": ["fork"]})

            if req_result.status_code == 202:
                print("Accepted for forking")
            else:
                print("Failed")
        else:
            print("Repository : %s already forked" % remote_path)

    def stash_fork(self, path):
        if not self.is_remote_fork(path, self.stash_api_url):
            req_result = requests.post(
                self.stash_api_url + "projects/ARIANE/repos/" + path,
                headers={"Content-Type": "application/json"},
                verify=False, auth=(self.user, self.password), data='{}')

            if req_result.status_code == 201:
                print("Forking repository : %s" % path)
        else:
            print("Repository : %s already forked" % path)

    def set_fork_ref_data(self):
        try:
            with open(self.main_ref) as fp:
                self.git_fork_repo_data = json.loads(fp.read())
            fp.close()
        except (OSError, IOError) as e:
            print("{0}".format(e))
            exit(0)

    def fork_repos(self, repo_type, plugin_name):
        print("*_* Tool will fork other repos for you *_* \n")
        for key, val in self.git_fork_repo_data.items():
            if repo_type == "core":
                if val["type"] == "core" or val["type"] == "environment":
                    path = val["url"]
                else:
                    continue
            else:
                if val["type"] == "plugin":
                    path = val["url"]
                else:
                    continue

            if "github" in self.netloc:
                self.git_fork(path)
            else:
                self.stash_fork(path.split("net.echinopsii.")[1])

    def set_vars(self, repo_type, plugin_name):
        parse_result = urlparse(self.URL)
        self.set_credentials()
        self.scheme = parse_result.scheme
        if '@' in parse_result.netloc:
            self.netloc = parse_result.netloc.split('@')[1]
        else:
            self.netloc = parse_result.netloc

        self.path = parse_result.path[:-4]

        self.set_fork_ref_data()
        if "github" in self.netloc:
            is_cloned = self.is_cloned(self.path, self.github_api_url)
            if not is_cloned:
                self.fork_repos(repo_type, plugin_name)
            self.generate_clone_ref(is_cloned)

        elif "stash" in self.netloc:
            is_cloned = self.is_cloned(self.path, self.stash_api_url)
            if not is_cloned:
                self.fork_repos(repo_type, plugin_name)
            self.generate_clone_ref(is_cloned)

    def read_config(self, repo_type, plugin_name=None):
        try:
            with open(self.script_path+'/.git/config') as git_config_obj:
                for line in git_config_obj.readlines():
                    if re.match("\turl", line):
                        self.URL = line.split("=")[1].strip()
                        break
        except (OSError, IOError) as e:
            print(self.script_path)
            print("{0}".format(e))
            exit(0)

        if self.URL:
            self.set_vars(repo_type, plugin_name)
        else:
            raise Exception("Can't find any URL")

    def fork_core(self):
        self.read_config("core")

    def fork_plugin(self, plugin_name):
        self.read_config("plugin", plugin_name)
