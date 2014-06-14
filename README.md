net.echinopsii.ariane.community.distrib
=======================================

Ariane Community Distribution Module


This module is the Ariane framework starter... It will help you to clone all necessary git projects and build a distribution.


Prerequisites :
===============

Before using Ariane distrib tool you need the following :

    + a Linux environment (not tested in other OS currently)
    + python 3.3 in your path
    + pip3 or python3-pip
    + .... in order to install requests (http://docs.python-requests.org/en/latest/ - pip3 install requests)
    + Java 1.7
    + git and maven in your path


Once all the requirements are meet you can execute the tool :

```
./distribManager.py -h
usage: distribManager.py [-h] {pluginmgr,pluginpkgr,distmgr,distpkgr} ...

Ariane distribution manager

positional arguments:
  {pluginmgr,pluginpkgr,distmgr,distpkgr}
                        sub commands help summary
    pluginmgr           [-h] (-l | -la plugin_name | -ld distribution_version)
    pluginpkgr          [-h] name version
    distmgr             [-h] (-d distribution_version | -l)
    distpkgr            [-h] version

optional arguments:
  -h, --help            show this help message and exit
```


Distribution manager :
======================

The distribution manager sub command helps you to manage Ariane distributions.

```
./distribManager.py distmgr -h
usage: distribManager.py distmgr [-h] (-d DETAILS | -l)

Manage supported Ariane distributions version

optional arguments:
  -h, --help            show this help message and exit
  -d DETAILS, --details DETAILS
                        Show supported distribution details
  -l, --list            List supported distribution version
```

```
./distribManager.py distmgr -l

List of Ariane distribution :

ariane.community.distrib-master.SNAPSHOT
```

```
./distribManager.py distmgr -d master.SNAPSHOT

Details of Ariane distribution master.SNAPSHOT :

Ariane component name                    Ariane component version
---------------------                    ------------------------
ariane.community.core.directory          master.SNAPSHOT
ariane.community.core.idm                master.SNAPSHOT
ariane.community.core.injector           master.SNAPSHOT
ariane.community.core.mapping            master.SNAPSHOT
ariane.community.core.portal             master.SNAPSHOT
ariane.community.environment             master.SNAPSHOT
ariane.community.installer               master.SNAPSHOT
```


Distribution packager :
=======================

The distribution packager sub command helps you to build Ariane distributions. It will clone all Ariane repositories (tag or master depending on the version you define),
build the libraries and package Ariane into a zip.

```
./distribManager.py distpkgr -h
usage: distribManager.py distpkgr [-h] version

Package a distribution

positional arguments:
  version     Ariane distribution version to package

optional arguments:
  -h, --help  show this help message and exit
```

```
./distribManager.py distpkgr master.SNAPSHOT
Ariane integration manager is working on your DEV environment
remote: Counting objects: 6, done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 6 (delta 2), reused 5 (delta 2)
Unpacking objects: 100% (6/6), done.
From https://github.com/echinopsii/net.echinopsii.ariane.community.core.injector
   fb105c6..e41c842  master     -> origin/master
Updating fb105c6..e41c842
Fast-forward
 pom.xml | 11 +++++++++++
 1 file changed, 11 insertions(+)
remote: Counting objects: 95, done.
remote: Compressing objects: 100% (63/63), done.
remote: Total 95 (delta 21), reused 27 (delta 4)
Unpacking objects: 100% (95/95), done.

.....


[INFO] ------------------------------------------------------------------------
[INFO] Building Ariane Community Distrib 0.5.0-SNAPSHOT
[INFO] ------------------------------------------------------------------------
[INFO]
[INFO] --- maven-clean-plugin:2.4.1:clean (default-clean) @ net.echinopsii.ariane ---
[INFO] Deleting /GITHUB/DEV/ariane/target
[INFO]
[INFO] --- maven-install-plugin:2.3.1:install (default-install) @ net.echinopsii.ariane ---
[INFO] Installing /GITHUB/DEV/ariane/pom.xml to /home/mffrench/.m2/repository/net/echinopsii/net.echinopsii.ariane/0.5.0-SNAPSHOT/net.echinopsii.ariane-0.5.0-SNAPSHOT.pom
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO]
[INFO] Ariane Community Installer ........................ SUCCESS [0.315s]
[INFO] Ariane Community Installer Tools .................. SUCCESS [3.901s]
[INFO] Ariane Community Core IDM Parent .................. SUCCESS [0.163s]
[INFO] Ariane Community Core IDM Base .................... SUCCESS [6.429s]
[INFO] Ariane Community Core Portal Parent ............... SUCCESS [0.026s]
[INFO] Ariane Community Core Portal Taitale Graph Render . SUCCESS [2.455s]
[INFO] Ariane Community Core Portal Web Resources ........ SUCCESS [1.278s]
[INFO] Ariane Community Core Portal Base ................. SUCCESS [3.832s]
[INFO] Ariane Community Core Portal IDM WebApp Tooling ... SUCCESS [4.545s]
[INFO] Ariane Community Core Portal WebApp Tooling ....... SUCCESS [3.230s]
[INFO] Ariane Community Core Portal WebApp Bundle ........ SUCCESS [3.385s]
[INFO] Ariane Community Core Directory Parent ............ SUCCESS [0.068s]
[INFO] Ariane Community Core Directory Base .............. SUCCESS [4.020s]
[INFO] Ariane Community Core Directory WebApp Tooling .... SUCCESS [6.403s]
[INFO] Ariane Community Core Injector Parent ............. SUCCESS [0.077s]
[INFO] Ariane Community Core Injector Base ............... SUCCESS [2.576s]
[INFO] Ariane Community Core Injector WebApp Tooling ..... SUCCESS [2.889s]
[INFO] Ariane Community Core Mapping Parent .............. SUCCESS [0.034s]
[INFO] Ariane Community Core Mapping DS .................. SUCCESS [0.045s]
[INFO] Ariane Community Core Mapping DS API .............. SUCCESS [2.341s]
[INFO] Ariane Community Core Mapping DS Mapper DSL ....... SUCCESS [18.949s]
[INFO] Ariane Community Core Mapping DS Blueprints Implementation  SUCCESS [2.430s]
[INFO] Ariane Community Core Mapping DS Runtime Injection Manager  SUCCESS [3.057s]
[INFO] Ariane Community Core Mapping WebApp Tooling ...... SUCCESS [2.622s]
[INFO] Ariane Community Distrib .......................... SUCCESS [0.224s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 1:17.025s
[INFO] Finished at: Sat Jun 14 11:51:16 CEST 2014
[INFO] Final Memory: 52M/403M
[INFO] ------------------------------------------------------------------------

Ariane distribution ariane.community.distrib-master.SNAPSHOT has been succesfully packaged in /home/mffrench/ariane.community.distrib-master.SNAPSHOT.zip

Ariane integration manager is working on your DEV environment

```


Then you're able to unzip the Ariane distrib and launch installer ([Ariane Community Installer Module](https://github.com/echinopsii/net.echinopsii.ariane.community.installer))