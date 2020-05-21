#!/bin/bash

if [ "x$USER" == "xroot" ]; then
    echo "DO NOT RUN SPADE AS ROOT"
    exit 0
fi

env | sort


source /cvmfs/grid.cern.ch/umd-c7ui-latest/etc/profile.d/setup-c7-ui-example.sh
# unset JRE_HOME
unset JAVA_HOME
# avoid wildfly/extras so we can upgrade 
export X509_USER_PROXY=/tmp/x509up_u213812
export JBOSS_CACERTS=/opt/spade/wildfly-15.0.1.Final/extras/cacerts
export X509_CERT_DIR=/etc/grid-security/certificates

JBOSS_TRUSTSTORE=""

if [ "X" != "X$JBOSS_CACERTS" ]; then 
    JBOSS_TRUSTSTORE="$JBOSS_TRUSTSTORE -Djavax.net.ssl.trustStore=$JBOSS_CACERTS" 
fi 

if [ "X" != "X$JBOSS_CACERTS_PASSWORD" ]; then 
    JBOSS_TRUSTSTORE="$JBOSS_TRUSTSTORE -Djavax.net.ssl.trustStorePassword=$JBOSS_CACERTS_PASSWORD" 
fi

env | sort

cd /opt/spade
/opt/spade/wildfly-15.0.1.Final/bin/standalone.sh -b=0.0.0.0 -bmanagement=0.0.0.0 $JBOSS_TRUSTSTORE
