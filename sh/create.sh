#!/bin/bash -x

exec 3>&1 # "save" stdout to fd 3
exec &>> /home/ec2-user/create.log

function error_exit() {
    echo "{\"Reason\": \"$1\"}" >&3 3>&- # echo reason to stdout (instead of log) and then close fd 3
    exit $2
}

if [ -z "${Event_ResourceProperties_Version}" ]
then
    error_exit "Version is required." 64
fi


AMI=$(/home/ec2-user/AMIFinder/findAMI.py -a ${Event_ResourceProperties_Version})
AMI_ret=$?
if [ $AMI_ret -ne 0 ]
then
    error_exit "Find AMI failed." $AMI_ret
else
    echo "{ \"PhysicalResourceId\" : \"$AMI\" }" >&3 3>&-  # echo success to stdout (instead of log) and then close fd 3
    exit 0
fi