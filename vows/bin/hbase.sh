#!/bin/sh

#be sure that hostname does not resolved as 127.0.1.1 in /etc/hosts cf : https://ria101.wordpress.com/2010/01/28/setup-hbase-in-pseudo-distributed-mode-and-connect-java-client/

#start Hbase Master + Zookeeper + HbaseRegionServer on localhost (127.0.0.1)
java -Xmx1000m -ea -XX:+UseConcMarkSweepGC -XX:+CMSIncrementalMode -Dhbase.log.dir=/usr/lib/hbase/bin/../logs -Dhbase.log.file=hbase.log -Dhbase.home.dir=/usr/lib/hbase/bin/.. -Dhbase.id.str= -Dhbase.root.logger=INFO,console -Djava.library.path=/usr/lib/hadoop-0.20/lib/native/Linux-amd64-64:/usr/lib/hbase/bin/../lib/native/Linux-amd64-64 -classpath `for i in /usr/lib/hbase/*.jar /usr/lib/hbase/lib/*.jar; do printf '%s:' $i; done` org.apache.hadoop.hbase.master.HMaster start >/dev/null 2>&1 &

#start Thrift hbase interface
java -Xmx1000m -ea -XX:+UseConcMarkSweepGC -XX:+CMSIncrementalMode -Dhbase.zookeeper.quorum=localhost:2181 -classpath `for i in /usr/lib/hbase/*.jar /usr/lib/hbase/lib/*.jar; do printf '%s:' $i; done` org.apache.hadoop.hbase.thrift.ThriftServer start >/dev/null 2>&1 &
