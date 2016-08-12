<Configuration>
    <Appenders>
        <Console name="CONSOLE" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{ABSOLUTE} | %-5.5p | %-16.16t | %-32.32c{1} | %X{bundle.id} - %X{bundle.name} - %X{bundle.version} | %m%n"/>
        </Console>
        <RollingFile name="LOG_FILE" fileName="${sys:karaf.data}/log/karaf.log"
              append="true" filePattern="${sys:karaf.data}/log/$${date:yyyy-MM}/fuse-%d{MM-dd-yyyy}-%i.log.gz">
           <PatternLayout>
             <Pattern>%d{ABSOLUTE} | %-5.5p | %-16.16t | %-32.32c{1} | %X{bundle.id} - %X{bundle.name} - %X{bundle.version} | %m%n</Pattern>
           </PatternLayout>
           <Policies>
                <TimeBasedTriggeringPolicy />
                <SizeBasedTriggeringPolicy size="250 MB"/>
            </Policies>
        </RollingFile>
        <PaxOsgi name="PAXOSGI" filter="VmLogAppender"/>
    </Appenders>
    <Loggers>
        <Root level="ERROR">
            <AppenderRef ref="CONSOLE"/>
            <AppenderRef ref="LOG_FILE"/>
            <AppenderRef ref="PAXOSGI"/>
        </Root>
        <logger level="ERROR" additivity="false" name="org.eclipse.jetty">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.messaging">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.cache">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.blueprintsimpl">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.dsl">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.sdsl">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.mdsl">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.rim">
            <appender-ref ref="LOG_FILE" />
        </logger>
        <logger level="INFO" additivity="false" name="net.echinopsii.ariane.community.core.mapping.ds.msgsrv">
            <appender-ref ref="LOG_FILE" />
        </logger>
    </Loggers>
</Configuration>
