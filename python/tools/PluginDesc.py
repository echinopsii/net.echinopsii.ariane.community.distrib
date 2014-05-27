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


class environment:

    def __init__(self, templateFP, defaultValuesFP, sqlScriptFP, targetConf, deployCmdFP):
        if templateFP is None or (os.path.exists(templateFP) and os.path.isfile(templateFP)):
            self.templateFP = templateFP
        else:
            raise FileNotFoundError(os.path.abspath(templateFP))

        if defaultValuesFP is None or (os.path.exists(defaultValuesFP) and os.path.isfile(defaultValuesFP)):
            self.defaultValuesFP = defaultValuesFP
        else:
            raise FileNotFoundError(os.path.abspath(defaultValuesFP))

        if sqlScriptFP is None or (os.path.exists(sqlScriptFP) and os.path.isfile(sqlScriptFP)):
            self.sqlScriptFP = sqlScriptFP
        else:
            raise FileNotFoundError(os.path.abspath(sqlScriptFP))

        if deployCmdFP is None or (os.path.exists(deployCmdFP) and os.path.isfile(deployCmdFP)):
            self.deployCmdFP = deployCmdFP
        else:
            print("File not found : " + os.path.abspath(deployCmdFP))
            raise FileNotFoundError(os.path.abspath(deployCmdFP))

        self.targetConf = targetConf

    def getDirectoryTemplateFP(self):
        return os.path.abspath(os.path.join(self.templateFP, os.pardir))

    def getDirectoryDefaultValuesFP(self):
        return os.path.abspath(os.path.join(self.defaultValuesFP, os.pardir))

    def getDirectorySqlScriptFP(self):
        return os.path.abspath(os.path.join(self.sqlScriptFP, os.pardir))

    def getDirectoryTargetConfFP(self):
        return os.path.abspath(os.path.join(self.targetConf, os.pardir))

    def getDirectoryTargetDeployCmdFP(self):
        return os.path.abspath(os.path.join(self.deployCmdFP, os.pardir))


class pluginDesc:

    def __init__(self, pluginDescPath):
        if os.path.exists(pluginDescPath) and os.path.isfile(pluginDescPath):
            jsonAddonDesc = json.load(open(pluginDescPath))

            self.id = jsonAddonDesc["id"]
            self.version = jsonAddonDesc["version"]
            self.type = jsonAddonDesc["type"]
            self.distribs = jsonAddonDesc["distribs"]
            self.hookPackage = jsonAddonDesc["hook"]["package"]
            self.hookModule = jsonAddonDesc["hook"]["module"]
            self.hookClass = jsonAddonDesc["hook"]["class"]
            self.environmentItems = []

            installerDir = pluginDescPath.split("installer/plugins")[0] + "/installer/"
            envDir = pluginDescPath.split("ariane")[0]
            for item in jsonAddonDesc["environment"]:
                absoluteDefaultValuesFP = None
                if item["defaultValuesFP"] != "None":
                    absoluteDefaultValuesFP = installerDir + item["defaultValuesFP"]

                absoluteTemplateFP = None
                if item["templateFP"] != "None":
                    absoluteTemplateFP = installerDir + item["templateFP"]

                absoluteSqlScriptFP = None
                if item["sqlScriptFP"] != "None":
                    absoluteSqlScriptFP = installerDir + item["sqlScriptFP"]

                absoluteDeployCmdFP = None
                if item["deployCmdFP"] != "None":
                    absoluteDeployCmdFP = installerDir + item["deployCmdFP"]

                absoluteTargetConf = None
                if item["targetConf"] != "None":
                    absoluteTargetConf = envDir + item["targetConf"]

                envItem = environment(absoluteTemplateFP, absoluteDefaultValuesFP, absoluteSqlScriptFP, absoluteTargetConf, absoluteDeployCmdFP)
                self.environmentItems.append(envItem)

        else:
            raise FileNotFoundError(os.path.abspath(pluginDescPath))