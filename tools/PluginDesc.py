# plugin description tools
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

__author__ = 'mffrench'


class Environment:

    def __init__(self, template_fp, default_values_fp, sql_script_fp, target_conf, deploy_cmd_fp):
        if template_fp is None or (os.path.exists(template_fp) and os.path.isfile(template_fp)):
            self.templateFP = template_fp
        else:
            raise FileNotFoundError(os.path.abspath(template_fp))

        if default_values_fp is None or (os.path.exists(default_values_fp) and os.path.isfile(default_values_fp)):
            self.defaultValuesFP = default_values_fp
        else:
            raise FileNotFoundError(os.path.abspath(default_values_fp))

        if sql_script_fp is None or (os.path.exists(sql_script_fp) and os.path.isfile(sql_script_fp)):
            self.sqlScriptFP = sql_script_fp
        else:
            raise FileNotFoundError(os.path.abspath(sql_script_fp))

        if deploy_cmd_fp is None or (os.path.exists(deploy_cmd_fp) and os.path.isfile(deploy_cmd_fp)):
            self.deployCmdFP = deploy_cmd_fp
        else:
            print("File not found : " + os.path.abspath(deploy_cmd_fp))
            raise FileNotFoundError(os.path.abspath(deploy_cmd_fp))

        self.targetConf = target_conf

    def get_directory_template_fp(self):
        return os.path.abspath(os.path.join(self.templateFP, os.pardir))

    def get_directory_default_values_fp(self):
        return os.path.abspath(os.path.join(self.defaultValuesFP, os.pardir))

    def get_directory_sql_script_fp(self):
        return os.path.abspath(os.path.join(self.sqlScriptFP, os.pardir))

    def get_directory_target_conf_fp(self):
        return os.path.abspath(os.path.join(self.targetConf, os.pardir))

    def get_directory_target_deploy_cmd_fp(self):
        return os.path.abspath(os.path.join(self.deployCmdFP, os.pardir))


class PluginDesc:

    def __init__(self, plugin_desc_path):
        if os.path.exists(plugin_desc_path) and os.path.isfile(plugin_desc_path):
            json_addon_desc = json.load(open(plugin_desc_path))

            self.id = json_addon_desc["id"]
            self.version = json_addon_desc["version"]
            self.type = json_addon_desc["type"]
            self.waitingStartString = json_addon_desc["waitingStartString"]
            self.distribs = json_addon_desc["distribs"]
            self.hookPackage = json_addon_desc["hook"]["package"]
            self.hookModule = json_addon_desc["hook"]["module"]
            self.hookClass = json_addon_desc["hook"]["class"]
            self.environmentItems = []

            installer_dir = plugin_desc_path.split("installer/plugins")[0] + "/installer/"
            env_dir = plugin_desc_path.split("ariane")[0]
            for item in json_addon_desc["environment"]:
                absolute_default_values_fp = None
                if item["defaultValuesFP"] != "None":
                    absolute_default_values_fp = installer_dir + item["defaultValuesFP"]

                absolute_template_fp = None
                if item["templateFP"] != "None":
                    absolute_template_fp = installer_dir + item["templateFP"]

                absolute_sql_script_fp = None
                if item["sqlScriptFP"] != "None":
                    absolute_sql_script_fp = installer_dir + item["sqlScriptFP"]

                absolute_deploy_cmd_fp = None
                if item["deployCmdFP"] != "None":
                    absolute_deploy_cmd_fp = installer_dir + item["deployCmdFP"]

                absolute_target_conf = None
                if item["targetConf"] != "None":
                    absolute_target_conf = env_dir + item["targetConf"]

                env_item = Environment(absolute_template_fp, absolute_default_values_fp, absolute_sql_script_fp,
                                       absolute_target_conf, absolute_deploy_cmd_fp)
                self.environmentItems.append(env_item)

        else:
            raise FileNotFoundError(os.path.abspath(plugin_desc_path))
