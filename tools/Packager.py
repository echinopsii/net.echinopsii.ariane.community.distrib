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
import json
import os
import shutil
import zipfile
from tools.PluginDesc import pluginDesc
from tools.DistributionRegistry import DistributionRegistry

__author__ = 'mffrench'


class Packager:

    def __init__(self, gitTarget, distribType, version, scriptPath,target="artifacts"):
        self.virgoDistributionName = "virgo-tomcat-server-3.6.2.RELEASE"
        self.distribType = distribType
        self.gitTarget = gitTarget
        self.version = version
        self.scriptPath=scriptPath
        self.home = os.path.expanduser("~")
        self.target = '/'.join(scriptPath.split('/')[:-1])+'/'+target
        ## clean installer => remove __pycache__ directories
        matches = []

        if self.version > "0.6.1":
            self.distribdir = "distrib"
            self.distribDBdir = "db"
        else:
            self.distribdir = "python"
            self.distribDBdir = "distrib"

        for root, dirnames, filenames in os.walk(self.gitTarget + "/ariane.community.installer/" + self.distribdir + "/installer"):
            for filename in fnmatch.filter(dirnames, "__pycache__"):
                matches.append(os.path.join(root, filename))
        for match in matches:
            shutil.rmtree(match)

    @staticmethod
    def copyModuleInstaller(source, target):
        if os.path.exists(source):
            for file in os.listdir(source):
                if os.path.isdir(source + "/" + file):
                    if os.path.exists(target + "/" + file):
                        Packager.copyModuleInstaller(source + "/" + file, target + "/" + file)
                    else:
                        shutil.copytree(source + "/" + file, target + "/" + file)
                else:
                    shutil.copy(source + "/" + file, target)

    @staticmethod
    def zipCoreDirectory(path, zip, distribname):
        for root, dirs, files in os.walk(path):
            for file in files:
                relativPath = distribname + "/" + root.split(path)[1] + "/" + file
                zip.write(os.path.join(root, file), arcname=relativPath)

    @staticmethod
    def zipAddonDirectory(path, zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                relativPath = root.split(path)[1] + "/" + file
                zip.write(os.path.join(root, file), arcname=relativPath)

    @staticmethod
    def myCopyTree(distribType, source, target):
        if distribType == "community":
            shutil.copytree(source, target)
        else:
            names = os.listdir(source)
            errors = []
            os.makedirs(target)
            pwd = os.getcwd()
            os.chdir(source)

            for name in names:
                srcname = os.path.join(source, name)
                dstname = os.path.join(target, name)
                try:
                    if os.path.islink(srcname):
                        linkto = os.readlink(srcname)
                        linktoabspath = os.path.abspath(linkto)
                        Packager.myCopyTree(distribType, linktoabspath, dstname)
                    elif os.path.isdir(srcname):
                        Packager.myCopyTree(distribType, srcname, dstname)
                    else:
                        shutil.copy2(srcname, dstname)
                except OSError as why:
                    errors.append((srcname, dstname, str(why)))
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
    def mergeTree(source, target):
        names = os.listdir(source)
        errors = []
        if os.path.isdir(source) and not os.path.exists(target):
            os.makedirs(target)
        pwd = os.getcwd()

        for name in names:
            srcname = os.path.join(source, name)
            dstname = os.path.join(target, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    Packager.mergeTree(srcname, dstname)
                else:
                    shutil.copy2(srcname, dstname)
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
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



    def buildDistrib(self):
        arianeDistribution = DistributionRegistry(self.distribType,self.scriptPath).getDistribution(self.version)
        if arianeDistribution is not None:
            arianeCoreModulesVersions = json.load(open(arianeDistribution.distribFile))

            targetTmpDistribPath = self.gitTarget + "/target/" + arianeDistribution.name
            if os.path.exists(targetTmpDistribPath):
                shutil.rmtree(targetTmpDistribPath)

            # copy dev env to tmp distrib
            #shutil.copytree(self.gitTarget + "/ariane." + self.distribType + ".environment/Virgo/" + self.virgoDistributionName, targetTmpDistribPath)
            Packager.myCopyTree(self.distribType, self.gitTarget + "/ariane." + self.distribType + ".environment/Virgo/" + self.virgoDistributionName, targetTmpDistribPath)

            # clean first
            shutil.rmtree(targetTmpDistribPath + "/ariane")
            if os.path.exists(targetTmpDistribPath + "/serviceability"):
                shutil.rmtree(targetTmpDistribPath + "/serviceability")
            if os.path.exists(targetTmpDistribPath + "/work"):
                shutil.rmtree(targetTmpDistribPath + "/work")
            for file in os.listdir(targetTmpDistribPath + "/repository/ariane-core/"):
                if fnmatch.fnmatch(file, "net.echinopsii.*plan*") or \
                        fnmatch.fnmatch(file, "net.echinopsii.*properties"):
                    os.remove(targetTmpDistribPath + "/repository/ariane-core/" + file)
            for file in os.listdir(targetTmpDistribPath + "/repository/ariane-plugins/"):
                os.remove(targetTmpDistribPath + "/repository/ariane-plugins/" + file)

            # push prod unix startup script
            os.remove(targetTmpDistribPath + "/bin/dmk.sh")
            os.remove(targetTmpDistribPath + "/bin/syncwebdev.sh")
            shutil.copy(self.scriptPath+"/resources/virgo/bin/dmk.sh", targetTmpDistribPath + "/bin/")

            # push prod log configuration
            os.remove(targetTmpDistribPath + "/configuration/serviceability.xml")
            shutil.copy(self.scriptPath+"/resources/virgo/configuration/serviceability." + self.distribType + ".xml", targetTmpDistribPath + "/configuration/serviceability.xml")

            # push Ariane repositories
            os.remove(targetTmpDistribPath + "/configuration/org.eclipse.virgo.repository.properties")
            shutil.copy(self.scriptPath+"/resources/virgo/configuration/org.eclipse.virgo.repository.properties", targetTmpDistribPath + "/configuration/")

            for module in arianeCoreModulesVersions.keys():
                if module != "ariane." + self.distribType + ".environment" and module != "ariane.community.installer":
                    version = arianeCoreModulesVersions[module]
                    moduleBuildsFile = self.gitTarget + "/" + module + "/" + self.distribdir + "/" + self.distribDBdir + "/resources/builds/" + module + "-" + version + ".json"
                    builds = json.load(open(moduleBuildsFile))
                    for build in builds:
                        shutil.copy(os.path.abspath(self.home + "/.m2/repository/" + build), targetTmpDistribPath + "/repository/ariane-core/")
                    shutil.copy(self.gitTarget + "/" + module + "/" + self.distribdir + "/" + self.distribDBdir + "/resources/virgo/repository/ariane-core/net.echinopsii." + module + "_" + version + ".plan", targetTmpDistribPath + "/repository/ariane-core/")

            # push Ariane installer
            os.mkdir(targetTmpDistribPath + "/ariane")
            # on DEV env. be sure that AddonDesc is same in installer as in distrib
            #if self.version != "master.SNAPSHOT":
            shutil.copy(self.scriptPath+"/tools/PluginDesc.py", self.gitTarget + "/ariane.community.installer/" + self.distribdir + "/installer/tools")
            shutil.copytree(self.gitTarget + "/ariane.community.installer/" + self.distribdir +  "/installer", targetTmpDistribPath + "/ariane/installer")
            for module in arianeCoreModulesVersions.keys():
                Packager.copyModuleInstaller(self.gitTarget + "/" + module + "/" + self.distribdir + "/installer", targetTmpDistribPath + "/ariane/installer")
            os.mkdir(targetTmpDistribPath + "/ariane/installer/lib")
            shutil.copy(self.home + "/.m2/repository/net/echinopsii/ariane/community/installer/net.echinopsii.ariane.community.installer.tools/0.1.0/net.echinopsii.ariane.community.installer.tools-0.1.0.jar",
                        targetTmpDistribPath + "/ariane/installer/lib")
            shutil.copy(self.home + "/.m2/repository/org/apache/mina/mina-core/2.0.7/mina-core-2.0.7.jar",
                        targetTmpDistribPath + "/ariane/installer/lib")
            shutil.copy(self.home + "/.m2/repository/org/apache/sshd/sshd-core/0.11.0/sshd-core-0.11.0.jar",
                        targetTmpDistribPath + "/ariane/installer/lib")
            shutil.copy(self.home + "/.m2/repository/org/slf4j/slf4j-api/1.6.6/slf4j-api-1.6.6.jar",
                        targetTmpDistribPath + "/ariane/installer/lib")

            Packager.mergeTree(self.gitTarget + "/ariane.community.core.portal/wresources/ariane/static", targetTmpDistribPath + "/ariane/static")
            Packager.mergeTree(self.gitTarget + "/ariane.community.core.mapping/taitale/ariane/static", targetTmpDistribPath + "/ariane/static")

            # zip package
            zipName = arianeDistribution.name + ".zip"
            zipf = zipfile.ZipFile(zipName, 'w')
            Packager.zipCoreDirectory(targetTmpDistribPath, zipf, arianeDistribution.name)
            zipf.close()

            os.makedirs(self.target, exist_ok=True)
            if os.path.exists(self.target + "/" + zipName):
                os.remove(self.target + "/" + zipName)
            shutil.move(zipName, self.target)
            print("\nAriane distribution " + arianeDistribution.name + " has been succesfully packaged in " + self.target + "/" + zipName + "\n")

            # remove working git target dir
            if self.version != "master.SNAPSHOT":
                shutil.rmtree(self.gitTarget)
            else:
                print("Ariane integration manager is working on your DEV environment")

        else:
            print("Provided distribution version " + self.version + " is not valid")

    def buildPlugin(self, pluginName):
        if self.version != "master.SNAPSHOT":
            pluginTarget = self.gitTarget + "/" + pluginName + "-" + self.version
        else:
            pluginTarget = self.gitTarget + "/" + pluginName

        if os.path.exists(pluginTarget):
            targetTmpDistribPath = pluginTarget + "/target/" + pluginName + "-" + self.version
            if os.path.exists(targetTmpDistribPath):
                shutil.rmtree(targetTmpDistribPath)
            #os.makedirs(targetTmpDistribPath + "/ariane/installer/plugins")
            os.makedirs(targetTmpDistribPath + "/repository/ariane-plugins")

            # push builds
            builds = json.load(open(pluginTarget + "/" + self.distribdir + "/" + self.distribDBdir + "/resources/builds/" + pluginName + "-" + self.version + ".json"))
            for build in builds:
                shutil.copy(os.path.abspath(self.home + "/.m2/repository/" + build), targetTmpDistribPath + "/repository/ariane-plugins/")
            shutil.copy(os.path.abspath(pluginTarget + "/" + self.distribdir + "/" + self.distribDBdir + "/resources/virgo/repository/ariane-plugins/net.echinopsii." + pluginName + "_" + self.version + ".plan"), targetTmpDistribPath + "/repository/ariane-plugins/")

            # push plugin installer
            isAddonInstallerFound = False
            for file in os.listdir(pluginTarget + "/" + self.distribdir + "/installer/plugins/"):
                abspath = pluginTarget + "/" + self.distribdir + "/installer/plugins/" + file
                print(abspath)
                if os.path.isdir(abspath):
                    arianepluginfile = abspath + "/arianeplugindesc.json"
                    description = pluginDesc(arianepluginfile)
                    if description.id == pluginName and description.version == self.version:
                        shutil.copytree(abspath, targetTmpDistribPath + "/ariane/installer/plugins/" + file)
                        for item in description.environmentItems:
                            if item.templateFP is not None:
                                itemTemplateDir = targetTmpDistribPath + "/ariane/installer/" + item.getDirectoryTemplateFP().split("installer")[1]
                                if not os.path.exists(itemTemplateDir):
                                    os.makedirs(itemTemplateDir)
                                shutil.copy(item.templateFP, itemTemplateDir)

                            if item.defaultValuesFP is not None:
                                itemDefaultValuesDir = targetTmpDistribPath + "/ariane/installer/" + item.getDirectoryDefaultValuesFP().split("installer")[1]
                                if not os.path.exists(itemDefaultValuesDir):
                                    os.makedirs(itemDefaultValuesDir)
                                shutil.copy(item.defaultValuesFP, itemDefaultValuesDir)

                            if item.sqlScriptFP is not None:
                                itemSqlScriptDir = targetTmpDistribPath + "/ariane/installer/" + item.getDirectorySqlScriptFP().split("installer")[1]
                                if not os.path.exists(itemSqlScriptDir):
                                    os.makedirs(itemSqlScriptDir)
                                shutil.copy(item.sqlScriptFP, itemSqlScriptDir)

                            if item.deployCmdFP is not None:
                                itemDeployCmdDir = targetTmpDistribPath + "/ariane/installer/" + item.getDirectoryTargetDeployCmdFP().split("installer")[1]
                                if not os.path.exists(itemDeployCmdDir):
                                    os.makedirs(itemDeployCmdDir)
                                shutil.copy(item.deployCmdFP, itemDeployCmdDir)

                        isAddonInstallerFound = True
                        break
                    else:
                        if file != "__pycache__":
                            print("[WARN] a plugin installer (" + file + ") is not following coding rule !")
                else:
                    if file != "__init__.py":
                        print("[WARN] pollution file (" + file + ") in installer")

            if not isAddonInstallerFound:
                raise RuntimeError("No installer found for plugin " + pluginName + " !")

            # zip package
            zipName = pluginName + "-" + self.version + ".zip"
            zipf = zipfile.ZipFile(zipName, 'w')
            Packager.zipAddonDirectory(targetTmpDistribPath, zipf)
            zipf.close()

            os.makedirs(self.target, exist_ok=True)
            if os.path.exists(self.target + "/" + zipName):
                os.remove(self.target + "/" + zipName)
            shutil.move(zipName, self.target)
            print("\nAriane plugin " + pluginName + "-" + self.version + " has been succesfully packaged in " + self.target + "/" + zipName + "\n")

            # remove working git target dir
            if self.version != "master.SNAPSHOT":
                shutil.rmtree(self.gitTarget)
            else:
                print("Ariane integration manager is working on your DEV environment")

        else:
            print("Unable to find plugin source folder " + pluginTarget + ". Has been the git repo cloned ?")
