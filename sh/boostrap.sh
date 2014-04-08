#!/bin/sh

#install aws-cfn-bridge
yum install git -y
git clone https://github.com/aws/aws-cfn-resource-bridge.git
cd aws-cfn-resource-bridge
python setup.py install

http://aws-emea.info.s3.amazonaws.com/resources/cfn-customresource-AMIFinder/cfn-resource-bridge

#download amifinder

