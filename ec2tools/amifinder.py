__author__ = 'stormacq@'

import boto.ec2
import logging

class AMIFinder:

    def __init__(self, logger=None):

        self.logger = logger or logging.getLogger(self.__class__.__name__)


        self.locales = { 'en' : 'English',
                         'fr' : 'French' }

        #shared connection object - but do not cache it as it is region dependant
        self.conn = None

        self.DEFAULT_FILTERS = { 'platform'           : 'windows',
                                 'architecture'       : 'x86_64',
                                 'root-device-type'   : 'ebs'}

        #cached complete AMI list for DEFAULT_FILTER
        self.amiList = None

    def searchDescription(self, image, search, locale):
        '''
            Search for matching string values in the image Description attribute

            This search function searches against the Base AMI only
        '''
        result = None

        if image.description is not None:
            if image.description.find('Base AMI') > -1:
                if image.description.find(locale) > -1:
                    if image.description.find(search) > -1:
                        result = image

        return result


    def findWindowsAMIInRegion(self, region, searchCriteria, locale='en'):
        '''
            Search for a Amazon's Base AMI Windows, 64 bits, EBS based in the specific region,
            the specific searchCriteria and the specific locale

            Typically, searchCriteria is the Windows version number (2012, 2008 SP1 ...)
        '''

        l = self.locales.get(locale);
        if l is None:
            self.logger.error('Unknown locale : %s' % locale)
            return None

        if boto.ec2.get_region(region) is None:
            self.logger.error('Invalid region : %s' % region)
            return None

        self.conn = boto.ec2.connect_to_region(region)

        if self.conn is None:
            self.logger.error('Can not connect to AWS')
            return None

        if (self.amiList is None):
            self.amiList = self.conn.get_all_images(owners='amazon', filters=self.DEFAULT_FILTERS)
            self.logger.debug('Retrieved %d images' % len(self.amiList))

            if len(self.amiList) < 1:
                self.logger.warning('No image retrieved for region "%s" using default filters (Windows, 64 Bits, EBS)' % region)
                return None

        result = None
        for image in self.amiList:
            #print image.description
            if self.searchDescription(image, searchCriteria, l) is not None:
                #print vars(image)
                result = image

        if result is not None:
            self.logger.debug('ImageID: %s ImageDescription: %s', result.id, result.description)
        else:
            self.logger.debug('ImageID: none')

        return result