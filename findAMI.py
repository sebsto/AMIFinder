#!/usr/bin/python

import sys, argparse, logging
import requests

from ec2tools import amifinder

__author__ = 'stormacq'
__version__ = 1.0

'''
Usage : findAMI --region <region_name>
                --version <version>
                --locale <two letters locale code> (default: 'en')

Find an Amazon's Windows Base AMI in the given region, the given version and for the given locale.
This command only search for 64bits EBS based AMI

Example : findAMI --region eu-west-1 --version '2012'
'''

logging.basicConfig()
logger = logging.getLogger('findAMI')
logger.setLevel(logging.INFO)
finder = amifinder.AMIFinder(logger)

def main(**kwargs):

    region = kwargs['region']
    if region is None:
        try:
            logger.warning('No region name given, trying to find one from EC2 instance meta data service')
            f = requests.get("http://169.254.169.254/latest/meta-data/placement/availability-zone/", timeout=1)
            region = f.text[:-1]
            logger.info('Using %s as region, provided by instance meta-data' % region)
        except requests.exceptions.Timeout:
            logger.error('Can not find region name (are you running this on EC2 ?). Abording.')
            sys.exit(-1)
        except:
            logger.error('Unknown error while trying to get region name. Abording.')
            sys.exit(-1)

    ami = finder.findWindowsAMIInRegion(region, kwargs['amiversion'], kwargs['locale'])
    if ami is not None:
        print ami.id
        sys.exit(0)
    else:
        sys.exit(-1)


if __name__ == '__main__':

    if sys.version_info < (2, 7):
        logger.info('Using Python < 2.7')
        parser = argparse.ArgumentParser(description='Find an Amazon Windows Base AMI')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s v' +
        str(__version__))
    else:
        parser = argparse.ArgumentParser(description='Find an Amazon Windows Base AMI', version='%(prog)s v' +
                                                                                            str(__version__))
    parser.add_argument('-r', '--region', type=str, help='Region name (default to local region when run on EC2)')
    parser.add_argument('-a', '--amiversion', type=str, help='String to search in version name (for example "2008" or '
                                                          '"2012 SP1")', required=True)
    parser.add_argument('-l', '--locale', type=str, default='en', help='Two letters locale name')
    args = parser.parse_args()
    main(**vars(args))
