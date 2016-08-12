################################################################################
#
#    Licensed to the Apache Software Foundation (ASF) under one or more
#    contributor license agreements.  See the NOTICE file distributed with
#    this work for additional information regarding copyright ownership.
#    The ASF licenses this file to You under the Apache License, Version 2.0
#    (the "License"); you may not use this file except in compliance with
#    the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
################################################################################

#
# Defines if the startlvl should be respected during feature startup. The default value is true. The default
# behavior for 2.x is false (!) for this property
#
# Be aware that this property is deprecated and will be removed in Karaf 4.0. So, if you need to
# set this to false, please use this only as a temporary solution!
#
#respectStartLvlDuringFeatureStartup=true


#
# Defines if the startlvl should be respected during feature uninstall. The default value is true.
# If true, means stop bundles respecting the descend order of start level in a certain feature.
#
#respectStartLvlDuringFeatureUninstall=true

#
# Comma separated list of features repositories to register by default
#
featuresRepositories = \
    mvn:org.apache.karaf.features/enterprise/4.0.3/xml/features, \
    mvn:org.apache.karaf.features/framework/4.0.3/xml/features, \
    mvn:org.apache.karaf.features/spring/4.0.3/xml/features, \
    mvn:org.apache.karaf.features/standard/4.0.3/xml/features, \
    http://repo1.maven.org/maven2/org/apache/felix/org.apache.felix.ipojo.features/1.12.1/org.apache.felix.ipojo.features-1.12.1.xml, \
    file:${karaf.home}system/com/typesafe/akka/2.3.14/net.echinopsii.3rdparty.akka-features-2.3.14.xml, \
    file:${karaf.home}system/org/infinispan/6.0.2/net.echinopsii.3rdparty.infinispan-features-6.0.2.xml, \
    file:${karaf.home}system/org/neo4j/net.echinopsii.3rdparty.neo4j.community/2.3.1/net.echinopsii.3rdparty.neo4j.community-features-2.3.1.xml, \
    file:${karaf.home}system/com/tinkerpop/2.6.231/net.echinopsii.3rdparty.tinkerpop-features-2.6.231.xml, \
    file:${karaf.home}system/net/echinopsii/ariane/community/messaging/0.2.1-SNAPSHOT/net.echinopsii.community.messaging-features-0.2.1.xml, \
    file:${karaf.home}system/net/echinopsii/ariane/community/core/mapping/0.8.1-MS-SNAPSHOT/net.echinopsii.community.core.mapping-back-features-0.8.1-MS-SNAPSHOT.xml



#
# Comma separated list of features to install at startup
#
featuresBoot = \
    aries-blueprint, \
    bundle, \
    config, \
    deployer, \
    diagnostic, \
    feature, \
    instance, \
    jaas, \
    kar, \
    log, \
    management, \
    package, \
    service, \
    shell, \
    shell-compat, \
    ssh, \
    system, \
    wrap, \
    ipojo, \
    typesafe.akka, \
    org.infinispan, \
    neo4j.community-server, \
    tinkerpop, \
    ariane.community.messaging, \
    ariane.community.core.mapping-back

#
# Defines if the boot features are started in asynchronous mode (in a dedicated thread)
#
featuresBootAsynchronous=false

#
# Service requirements enforcement
#
# By default, the feature resolver checks the service requirements/capabilities of
# bundles for new features (xml schema >= 1.3.0) in order to automatically installs
# the required bundles.
# The following flag can have those values:
#   - disable: service requirements are completely ignored
#   - default: service requirements are ignored for old features
#   - enforce: service requirements are always verified
#
#serviceRequirements=default
