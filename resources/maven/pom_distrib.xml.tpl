<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- General information -->
    <groupId>net.echinopsii</groupId>
    <artifactId>net.echinopsii.ariane</artifactId>
    <version>{{ version }}</version>
    <name>Ariane Community Distrib</name>
    <packaging>pom</packaging>

    <modules>
    {% for m in modules %}
    {% if m.type == 'core' %}
    <module>ariane.community.core.{{ m.name }}</module>
    {% else %}
    <module>ariane.community.{{ m.name }}</module>
    {% endif %}
    {% endfor %}
    </modules>

</project>
