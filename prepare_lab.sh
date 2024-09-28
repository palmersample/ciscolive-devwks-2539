#!/bin/sh

if [ "x${DNS_DOMAIN}" = "x" ]; then
  echo ""
  echo "******************************************************************************"
  echo "FATAL ERROR:"
  echo "  DNS_DOMAIN environment variable not set, unable to proceed!"
  echo ""
  echo "  Ensure you completed the workshop setup task to setup the environment,"
  echo "  or supply the DNS_DOMAIN variable when calling this script."
  echo "******************************************************************************"
  echo ""
  kill -INT $$
fi

[ ! -d "./ssh" ] && mkdir ./ssh
NETCONF_SSH_CONFIG_FILE="./ssh/netconf_ssh_config"
SSH_CONFIG_FILE="./ssh/ssh_config"

TIMEOUT_CMD=`which timeout`

ERROR_COUNT=0
ERROR_MESSAGES=""

TIMEOUT_CMD=`which timeout`
if [ $? -eq 0 ]; then
  TIMEOUT_CMD="${TIMEOUT_CMD} 5 "
else
  TIMEOUT_CMD=""
fi

test_proxy()
{
  printf "%40s" "Proxy status: "
  PROXY_CONNECT_RESULT=$(echo "" | ${TIMEOUT_CMD}openssl s_client -connect ${PROXY_DNS_NAME}:443 -tls1_2 2>&1 > /dev/null)
  if [ $? -ne 0 ] ; then
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- Unable to contact the proxy server.\n"
    echo "FAIL"
  else
    echo "OK"
  fi
}

test_router()
{
  # Expect an "Unauthorized" result
  RESTCONF_TARGET=401

  printf "%40s" "IOSXE SSH Status: "
  SSH_PROXY_RESULT=$(${TIMEOUT_CMD}ssh \
    -o ProxyCommand="openssl s_client -quiet -servername ${RTR_DNS_NAME} -connect ${PROXY_DNS_NAME}:${PROXY_SSH_PORT}" \
    -o 'BatchMode=yes' \
    -o 'ConnectionAttempts=1' \
    -o "StrictHostKeyChecking=no" \
    dummy@${RTR_DNS_NAME} -p 8000 2>&1 > /dev/null
  )
  SSH_STATUS=$(grep -i "permission denied" <<<${SSH_PROXY_RESULT})
  if [ $? -ne 0 ]; then
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- IOSXE SSH is not accessible.\n"
    echo "FAIL"
  else
    echo "OK"
  fi

  printf "%40s" "IOSXE NETCONF Status: "
  NETCONF_PROXY_RESULT=$(${TIMEOUT_CMD}ssh \
    -o ProxyCommand="openssl s_client -quiet -servername ${RTR_DNS_NAME} -connect ${PROXY_DNS_NAME}:${PROXY_NETCONF_PORT}" \
    -o 'BatchMode=yes' \
    -o 'ConnectionAttempts=1' \
    -o "StrictHostKeyChecking=no" \
    dummy@${RTR_DNS_NAME} \
    -p 830 NETCONF 2>&1 > /dev/null)
  NETCONF_STATUS=$(grep -i "permission denied" <<<${NETCONF_PROXY_RESULT})
  if [ $? -ne 0 ]; then
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- IOSXE NETCONF is not accessible.\n"
    echo "FAIL"
  else
    echo "OK"
  fi

  printf "%40s" "IOSXE RESTCONF Status: "
  RESTCONF_RESULT=$(${TIMEOUT_CMD}curl -s -o /dev/null -w "%{http_code}" \
    "${RTR_URL}/restconf"
  )
  if [ "x${RESTCONF_RESULT}" = "x${RESTCONF_TARGET}" ]; then
    echo "OK"
  else
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- IOSXE RESTCONF is not accessible.\n"
    echo "FAIL"
  fi
}

generate_ssh_config()
{
  printf "%40s" "NETCONF proxy: "
  # Generate NETCONF SSH Proxy Config file
  echo "Host *.${DNS_DOMAIN}" > ${NETCONF_SSH_CONFIG_FILE}
  echo "  ProxyCommand openssl s_client -quiet -servername %h -connect ${PROXY_DNS_NAME}:${PROXY_NETCONF_PORT}" >> ${NETCONF_SSH_CONFIG_FILE}
  echo "  StrictHostKeyChecking no" >> ${NETCONF_SSH_CONFIG_FILE}

  if [ -f ${NETCONF_SSH_CONFIG_FILE} ]; then
    echo "OK"
  else
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- NETCONF SSH Proxy config not created.\n"
    echo "FAIL"
  fi

  printf "%40s" "SSH proxy: "
  # Generate SSH Proxy Config file
  echo "Host *.${DNS_DOMAIN}" > ${SSH_CONFIG_FILE}
  echo "  ProxyCommand openssl s_client -quiet -servername %h -connect ${PROXY_DNS_NAME}:${PROXY_SSH_PORT}" >> ${SSH_CONFIG_FILE}
  echo "  StrictHostKeyChecking no" >> ${SSH_CONFIG_FILE}
  if [ -f ${SSH_CONFIG_FILE} ]; then
    echo "OK"
  else
    ERROR_COUNT=${ERROR_COUNT+1}
    ERROR_MESSAGES="${ERROR_MESSAGES}\t- SSH Proxy config not created.\n"
    echo "FAIL"
  fi

}


echo "GET READY FOR YOUR CISCO LIVE WORKSHOP EXPERIENCE! :)"
echo ""

echo -n "What is your pod number? "
read POD_NUMBER
POD_NUMBER=$(echo ${POD_NUMBER} | sed 's/^0*//')

PROXY_DNS_NAME="proxy.${DNS_DOMAIN}"
PROXY_SSH_PORT=8000
PROXY_NETCONF_PORT=8300

RTR_DNS_NAME="pod${POD_NUMBER}-rtr.${DNS_DOMAIN}"
RTR_URL="https://${RTR_DNS_NAME}"

echo ""
echo "************************************************************************"

echo ""
echo "TEST 1: Checking connectivity to the proxy for Pod ${POD_NUMBER}"
test_proxy

echo ""
echo "TEST 2: Checking connectivity to IOSXE in Pod ${POD_NUMBER}:"
test_router

echo ""
echo "SETUP: Generate SSH configuration files for Pod ${POD_NUMBER}"
generate_ssh_config

echo ""
if [ ${ERROR_COUNT} -gt 0 ]; then
  echo "THERE WERE ERRORS IN SETUP TESTING:"
  printf "${ERROR_MESSAGES}\n"
  printf "\tPlease ask your proctor for assistance!\n"
else
  echo "ALL SETUP TASKS OK - Time to have some automation fun!"
  export RTR_DNS_NAME=${RTR_DNS_NAME}
  export PROXY_DNS_NAME=${PROXY_DNS_NAME}
  export PROXY_SSH_PORT=8000
fi

echo ""
