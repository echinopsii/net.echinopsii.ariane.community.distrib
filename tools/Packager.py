# Ariane distribution packager
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
import fnmatch
import glob
import json
import os
import shutil
import zipfile
import time
from tools.Distribution import Distribution
from tools.PluginDesc import PluginDesc
from tools.DistributionRegistry import DistributionRegistry

__author__ = 'mffrench'


class Packager:

    def __init__(self, git_target, distrib_type, distrib_version, distrib_dep_type, script_path,
                 target="artifacts", plugin_version="core"):
        self.virgo_distribution_name = "virgo-tomcat-server-3.6.2.RELEASE"
        self.distrib_type = distrib_type
        self.distrib_dep_type = distrib_dep_type
        self.git_target = git_target
        if plugin_version == "core":
            self.version = distrib_version
            if 'SNAPSHOT' in distrib_version and 'master' not in distrib_version:
                self.distrib_version = self.version.split('.SNAPSHOT')[0]
            else:
                self.distrib_version = self.version
        else:
            self.version = plugin_version
            if 'SNAPSHOT' in self.version and 'master' not in self.version:
                self.plugin_version = self.version.split('.SNAPSHOT')[0]
            else:
                self.plugin_version = self.version
            self.distrib_version = distrib_version
        self.script_path = script_path
        self.home = os.path.expanduser("~")
        self.target = '/'.join(script_path.split('/')[:-1])+'/'+target
        ## clean installer => remove __pycache__ directories
        matches = []

        if distrib_version > "0.6.1":
            self.distrib_dir = "distrib"
            self.distrib_db_dir = "db"
        else:
            self.distrib_dir = "python"
            self.distrib_db_dir = "distrib"

        for root, dir_names, file_names in \
                os.walk(self.git_target + "/ariane.community.installer/" + self.distrib_dir + "/installer"):
            for filename in fnmatch.filter(dir_names, "__pycache__"):
                matches.append(os.path.join(root, filename))
        for match in matches:
            shutil.rmtree(match)

    @staticmethod
    def copy_module_installer(source, target):
        if os.path.exists(source):
            for file in os.listdir(source):
                if os.path.isdir(source + "/" + file):
                    if os.path.exists(target + "/" + file):
                        Packager.copy_module_installer(source + "/" + file, target + "/" + file)
                    else:
                        shutil.copytree(source + "/" + file, target + "/" + file)
                else:
                    shutil.copy(source + "/" + file, target)

    @staticmethod
    def zip_core_directory(path, to_zip, distrib_name):
        for root, dirs, files in os.walk(path):
            for file in files:
                relative_path = distrib_name + "/" + root.split(path)[1] + "/" + file
                to_zip.write(os.path.join(root, file), arcname=relative_path)

    @staticmethod
    def zip_addon_directory(path, to_zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                relative_path = root.split(path)[1] + "/" + file
                to_zip.write(os.path.join(root, file), arcname=relative_path)

    @staticmethod
    def my_copy_tree(distrib_type, source, target):
        if distrib_type == "community":
            shutil.copytree(source, target)
        else:
            names = os.listdir(source)
            errors = []
            os.makedirs(target)
            pwd = os.getcwd()
            os.chdir(source)

            for name in names:
                src_name = os.path.join(source, name)
                dst_name = os.path.join(target, name)
                try:
                    if os.path.islink(src_name):
                        link_to = os.readlink(src_name)
                        link_to_abs_path = os.path.abspath(link_to)
                        Packager.my_copy_tree(distrib_type, link_to_abs_path, dst_name)
                    elif os.path.isdir(src_name):
                        Packager.my_copy_tree(distrib_type, src_name, dst_name)
                    else:
                        shutil.copy2(src_name, dst_name)
                except OSError as why:
                    errors.append((src_name, dst_name, str(why)))
                except shutil.Error as err:
                    errors.extend(err.args[0])

            os.chdir(pwd)

            try:
                shutil.copystat(source, target)
            except shutil.WindowsError:
                # can't copy file access times on Windows
                pass
            except OSError as why:
                errors.extend((source, target, str(why)))
            if errors:
                raise shutil.Error(errors)

    @staticmethod
    def merge_tree(source, target):
        names = os.listdir(source)
        errors = []
        if os.path.isdir(source) and not os.path.exists(target):
            os.makedirs(target)
        pwd = os.getcwd()

        for name in names:
            src_name = os.path.join(source, name)
            dst_name = os.path.join(target, name)
            try:
                if os.path.islink(src_name):
                    link_to = os.readlink(src_name)
                    os.symlink(link_to, dst_name)
                elif os.path.isdir(src_name):
                    Packager.merge_tree(src_name, dst_name)
                else:
                    shutil.copy2(src_name, dst_name)
            except OSError as why:
                errors.append((src_name, dst_name, str(why)))
            except shutil.Error as err:
                errors.extend(err.args[0])

        os.chdir(pwd)

        try:
            shutil.copystat(source, target)
        except shutil.WindowsError:
            # can't copy file access times on Windows
            pass
        except OSError as why:
            errors.extend((source, target, str(why)))
            if errors:
                raise shutil.Error(errors)

    def build_virgo_tomcat_env(self, target_tmp_distrib_path, ariane_core_modules_versions, ariane_distribution):
        # copy dev env to tmp distrib
        #shutil.copytree(self.gitTarget + "/ariane." + self.distribType + ".environment/Virgo/" +
        # self.virgoDistributionName, targetTmpDistribPath)
        Packager.my_copy_tree(self.distrib_type, self.git_target + "/ariane." + self.distrib_type +
                              ".environment/Virgo/" + self.virgo_distribution_name, target_tmp_distrib_path)

        # clean first
        shutil.rmtree(target_tmp_distrib_path + "/ariane")
        if os.path.exists(target_tmp_distrib_path + "/serviceability"):
            shutil.rmtree(target_tmp_distrib_path + "/serviceability")
        if os.path.exists(target_tmp_distrib_path + "/work"):
            shutil.rmtree(target_tmp_distrib_path + "/work")
        for file in os.listdir(target_tmp_distrib_path + "/repository/ariane-core/"):
            if fnmatch.fnmatch(file, "net.echinopsii.*plan*") or \
                    fnmatch.fnmatch(file, "net.echinopsii.*properties"):
                os.remove(target_tmp_distrib_path + "/repository/ariane-core/" + file)
        for file in os.listdir(target_tmp_distrib_path + "/repository/ariane-plugins/"):
            os.remove(target_tmp_distrib_path + "/repository/ariane-plugins/" + file)

        # push prod unix startup script
        os.remove(target_tmp_distrib_path + "/bin/dmk.sh")
        if ariane_distribution.version > "0.8.0":
            os.remove(target_tmp_distrib_path + "/bin/setenv-frt.sh")
            os.remove(target_tmp_distrib_path + "/bin/setenv-mno.sh")
            os.remove(target_tmp_distrib_path + "/bin/syncwebdev.sh")
        shutil.copy(self.script_path+"/resources/virgo/bin/dmk.sh", target_tmp_distrib_path + "/bin/")
        if ariane_distribution.version > "0.8.0":
            with open(target_tmp_distrib_path + "/bin/setenv.sh", "w") as setenv_file:
                setenv_file.write("DEPLOY=%s" % ariane_distribution.dep_type)

        # push prod log configuration
        os.remove(target_tmp_distrib_path + "/configuration/serviceability.xml")
        shutil.copy(self.script_path+"/resources/virgo/configuration/serviceability." + self.distrib_type + ".xml",
                    target_tmp_distrib_path + "/configuration/serviceability.xml")

        # push Ariane repositories
        os.remove(target_tmp_distrib_path + "/configuration/org.eclipse.virgo.repository.properties")
        shutil.copy(self.script_path+"/resources/virgo/configuration/org.eclipse.virgo.repository.properties",
                    target_tmp_distrib_path + "/configuration/")

        for module in ariane_core_modules_versions.keys():
            if module != "ariane." + self.distrib_type + ".environment" and module != "ariane.community.installer":
                if ariane_distribution.dep_type == Distribution.MNO_DEPLOYMENT_TYPE:
                    dep_version = ariane_core_modules_versions[module]
                else:
                    dep_version = ariane_distribution.dep_type + "-" + ariane_core_modules_versions[module]

                if ariane_distribution.dep_type != Distribution.MNO_DEPLOYMENT_TYPE and \
                        not os.path.isfile(self.git_target + "/" + module + "/" + self.distrib_dir + "/" +
                                                   self.distrib_db_dir + "/resources/builds/" + module + "-" +
                                                   dep_version + ".json"):
                    dep_version = ariane_core_modules_versions[module]

                module_builds_file = self.git_target + "/" + module + "/" + self.distrib_dir + "/" + \
                                     self.distrib_db_dir + "/resources/builds/" + module + "-" + dep_version + ".json"
                builds = json.load(open(module_builds_file))
                for build in builds:
                    shutil.copy(os.path.abspath(self.home + "/.m2/repository/" + build), target_tmp_distrib_path +
                                "/repository/ariane-core/")

                dep_version = dep_version.replace("-", "_")

                if ariane_distribution.dep_type != Distribution.MNO_DEPLOYMENT_TYPE and \
                        not os.path.isfile(self.git_target + "/" + module + "/" + self.distrib_dir + "/" +
                                                   self.distrib_db_dir +
                                                   "/resources/virgo/repository/ariane-core/net.echinopsii." + module +
                                                   "_" + dep_version + ".plan"):
                    dep_version = ariane_core_modules_versions[module]

                shutil.copy(self.git_target + "/" + module + "/" + self.distrib_dir + "/" + self.distrib_db_dir +
                            "/resources/virgo/repository/ariane-core/net.echinopsii." + module + "_" + dep_version +
                            ".plan", target_tmp_distrib_path + "/repository/ariane-core/")

        for file in os.listdir(target_tmp_distrib_path + "/repository/ariane-core/"):
            file_match = "*tpl"
            if fnmatch.fnmatch(file, file_match):
                os.remove(target_tmp_distrib_path + "/repository/ariane-core/" + file)

        Packager.merge_tree(self.git_target +
                            "/ariane.community.core.portal/wresources/src/main/webapp/ariane/static",
                            target_tmp_distrib_path + "/ariane/static")
        portal_wresources_target_dir = glob.glob(self.git_target +
                                                 "/ariane.community.core.portal/wresources/target/*/ariane/static")
        Packager.merge_tree(portal_wresources_target_dir[0], target_tmp_distrib_path + "/ariane/static")

        Packager.merge_tree(self.git_target +
                            "/ariane.community.core.mapping/taitale/src/main/webapp/ariane/static",
                            target_tmp_distrib_path + "/ariane/static")
        mapping_taitale_target_dir = glob.glob(self.git_target +
                                               "/ariane.community.core.mapping/taitale/target/*/ariane/static")
        Packager.merge_tree(mapping_taitale_target_dir[0], target_tmp_distrib_path + "/ariane/static")

    def build_karaf_env(self):
        pass

    def build_core_installer_env(self, target_tmp_distrib_path, ariane_core_modules_versions, ariane_distribution):
        # push Ariane installer
        # os.mkdir(target_tmp_distrib_path + "/ariane")
        # on DEV env. be sure that AddonDesc is same in installer as in distrib
        # if self.version != "master.SNAPSHOT":
        shutil.copy(self.script_path+"/tools/PluginDesc.py", self.git_target + "/ariane.community.installer/" +
                    self.distrib_dir + "/installer/tools")
        shutil.copytree(self.git_target + "/ariane.community.installer/" + self.distrib_dir + "/installer",
                        target_tmp_distrib_path + "/ariane/installer")
        for module in ariane_core_modules_versions.keys():
            Packager.copy_module_installer(self.git_target + "/" + module + "/" + self.distrib_dir + "/installer",
                                           target_tmp_distrib_path + "/ariane/installer")
        os.mkdir(target_tmp_distrib_path + "/ariane/installer/lib")
        shutil.copy(self.home +
                    "/.m2/repository/net/echinopsii/ariane/community/installer/"
                    "net.echinopsii.ariane.community.installer.tools/0.1.0/"
                    "net.echinopsii.ariane.community.installer.tools-0.1.0.jar",
                    target_tmp_distrib_path + "/ariane/installer/lib")
        shutil.copy(self.home + "/.m2/repository/org/apache/mina/mina-core/2.0.7/mina-core-2.0.7.jar",
                    target_tmp_distrib_path + "/ariane/installer/lib")
        shutil.copy(self.home + "/.m2/repository/org/apache/sshd/sshd-core/0.11.0/sshd-core-0.11.0.jar",
                    target_tmp_distrib_path + "/ariane/installer/lib")
        shutil.copy(self.home + "/.m2/repository/org/slf4j/slf4j-api/1.6.6/slf4j-api-1.6.6.jar",
                    target_tmp_distrib_path + "/ariane/installer/lib")

        dist_ctx_json = open(target_tmp_distrib_path + "/ariane/id.json", "w")
        dist_ctx = {
            "version": self.distrib_version,
            "deployment_type": ariane_distribution.dep_type,
            "delivery_date": time.strftime("%x")
        }
        dist_ctx_json_str = json.dumps(dist_ctx, sort_keys=True, indent=4, separators=(',', ': '))
        dist_ctx_json.write(dist_ctx_json_str)
        dist_ctx_json.close()

    def zip_core_and_clean(self, target_tmp_distrib_path, ariane_distribution):
        # zip package
        zip_name = ariane_distribution.name + ".zip"
        zip_path = self.git_target + "/target/" + zip_name
        zip_file = zipfile.ZipFile(zip_path, 'w')
        Packager.zip_core_directory(target_tmp_distrib_path, zip_file, ariane_distribution.name)
        zip_file.close()

        os.makedirs(self.target, exist_ok=True)
        if os.path.exists(self.target + "/" + zip_name):
            os.remove(self.target + "/" + zip_name)
        shutil.move(zip_path, self.target)
        print("\nAriane distribution " + ariane_distribution.name + " has been succesfully packaged in " +
              self.target + "/" + zip_name + "\n")

        # remove working git target dir
        if 'SNAPSHOT' not in self.version:
            shutil.rmtree(self.git_target)
        else:
            print("Ariane integration manager is working on your DEV environment")

    def build_distrib(self):
        ariane_distribution = DistributionRegistry(self.distrib_type, self.script_path).\
            get_distribution(self.distrib_version, dep_type=self.distrib_dep_type)
        if ariane_distribution is not None:
            ariane_core_modules_versions = json.load(open(ariane_distribution.distrib_file))

            target_tmp_distrib_path = self.git_target + "/target/" + ariane_distribution.name
            if os.path.exists(target_tmp_distrib_path):
                shutil.rmtree(target_tmp_distrib_path)

            self.build_virgo_tomcat_env(target_tmp_distrib_path, ariane_core_modules_versions, ariane_distribution)
            self.build_core_installer_env(target_tmp_distrib_path, ariane_core_modules_versions, ariane_distribution)
            self.zip_core_and_clean(target_tmp_distrib_path, ariane_distribution)
        else:
            print("Provided distribution version " + self.version + " is not valid")

    def build_plugin(self, plugin_name):
        if 'SNAPSHOT' not in self.version:
            plugin_target = self.git_target + "/" + plugin_name + "-" + self.version
        else:
            plugin_target = self.git_target + "/" + plugin_name

        if os.path.exists(plugin_target):
            target_tmp_distrib_path = plugin_target + "/target/" + plugin_name + "-" + self.plugin_version
            if os.path.exists(target_tmp_distrib_path):
                shutil.rmtree(target_tmp_distrib_path)
            #os.makedirs(targetTmpDistribPath + "/ariane/installer/plugins")
            os.makedirs(target_tmp_distrib_path + "/repository/ariane-plugins")

            # push builds
            if os.path.exists(plugin_target + "/" + self.distrib_dir + "/" + self.distrib_db_dir +
                              "/resources/builds/" + plugin_name + "-" + self.plugin_version + ".json"):
                builds = json.load(open(plugin_target + "/" + self.distrib_dir + "/" + self.distrib_db_dir +
                                        "/resources/builds/" + plugin_name + "-" + self.plugin_version + ".json"))
                for build in builds:
                    shutil.copy(os.path.abspath(self.home + "/.m2/repository/" + build), target_tmp_distrib_path +
                                "/repository/ariane-plugins/")
                shutil.copy(os.path.abspath(plugin_target + "/" + self.distrib_dir + "/" + self.distrib_db_dir +
                                            "/resources/virgo/repository/ariane-plugins/net.echinopsii." + plugin_name +
                                            "_" + self.plugin_version + ".plan"),
                            target_tmp_distrib_path + "/repository/ariane-plugins/")

            # push plugin installer
            is_addon_installer_found = False
            for file in os.listdir(plugin_target + "/" + self.distrib_dir + "/installer/plugins/"):
                abspath = plugin_target + "/" + self.distrib_dir + "/installer/plugins/" + file
                if os.path.isdir(abspath):
                    ariane_plugin_file = abspath + "/arianeplugindesc.json"
                    description = PluginDesc(ariane_plugin_file)
                    if description.id == plugin_name and description.version == self.plugin_version:
                        shutil.copytree(abspath, target_tmp_distrib_path + "/ariane/installer/plugins/" + file)
                        for item in description.environmentItems:
                            if item.templateFP is not None:
                                item_template_dir = target_tmp_distrib_path + "/ariane/installer/" + \
                                                    item.get_directory_template_fp().split("installer")[1]
                                if not os.path.exists(item_template_dir):
                                    os.makedirs(item_template_dir)
                                shutil.copy(item.templateFP, item_template_dir)

                            if item.defaultValuesFP is not None:
                                item_default_values_dir = target_tmp_distrib_path + "/ariane/installer/" + \
                                                          item.get_directory_default_values_fp().split("installer")[1]
                                if not os.path.exists(item_default_values_dir):
                                    os.makedirs(item_default_values_dir)
                                shutil.copy(item.defaultValuesFP, item_default_values_dir)

                            if item.sqlScriptFP is not None:
                                item_sql_script_dir = target_tmp_distrib_path + "/ariane/installer/" + \
                                                      item.get_directory_sql_script_fp().split("installer")[1]
                                if not os.path.exists(item_sql_script_dir):
                                    os.makedirs(item_sql_script_dir)
                                shutil.copy(item.sqlScriptFP, item_sql_script_dir)

                            if item.deployCmdFP is not None:
                                item_deploy_cmd_dir = target_tmp_distrib_path + "/ariane/installer/" + \
                                                      item.get_directory_target_deploy_cmd_fp().split("installer")[1]
                                if not os.path.exists(item_deploy_cmd_dir):
                                    os.makedirs(item_deploy_cmd_dir)
                                shutil.copy(item.deployCmdFP, item_deploy_cmd_dir)

                        is_addon_installer_found = True
                        break
                    else:
                        if file != "__pycache__":
                            print("[WARN] a plugin installer (" + file + ") is not following coding rule !")
                else:
                    if file != "__init__.py":
                        print("[WARN] pollution file (" + file + ") in installer")

            if not is_addon_installer_found:
                raise RuntimeError("No installer found for plugin " + plugin_name + " !")

            # zip package
            zip_name = plugin_name + "-" + self.plugin_version + ".zip"
            if not os.path.exists(self.git_target + "/target/"):
                os.mkdir(self.git_target + "/target/")
            zip_path = self.git_target + "/target/" + zip_name
            zip_file = zipfile.ZipFile(zip_path, 'w')
            Packager.zip_addon_directory(target_tmp_distrib_path, zip_file)
            zip_file.close()

            os.makedirs(self.target, exist_ok=True)
            if os.path.exists(self.target + "/" + zip_name):
                os.remove(self.target + "/" + zip_name)
            shutil.move(zip_path, self.target)
            print("\nAriane plugin " + plugin_name + "-" + self.version + " has been successfully packaged in " +
                  self.target + "/" + zip_name + "\n")

            # remove working git target dir
            if 'SNAPSHOT' not in self.version:
                shutil.rmtree(self.git_target)
            else:
                print("Ariane integration manager is working on your DEV environment")

        else:
            print("Unable to find plugin source folder " + plugin_target + ". Has been the git repo cloned ?")
