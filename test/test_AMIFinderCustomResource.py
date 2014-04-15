__author__ = 'stormacq'

import unittest, logging
import datetime, time
import pystache
import boto.cloudformation

from findAMI import AMIFinder


class AMIFinderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig()
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)

    def createCustomResource(self, region):
        # read template
        with open ("cfn/amifinder.template.json", "r") as cfnTemplateFile:
            data=cfnTemplateFile.read()

        # connect to the appropriate region
        conn = boto.cloudformation.connect_to_region(region)

        # create the stack
        now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
        stackID = conn.create_stack(stack_name='AMIFinderCustomResource-' + now, template_body=data)
        stack = conn.describe_stacks(stackID)[0]
        #print vars(stack)
        self.logger.debug('Waiting for Custom Resource Stack to be created')
        while stack.stack_status == 'CREATE_IN_PROGRESS':
            self.logger.debug('.')
            time.sleep(10)
            stack = conn.describe_stacks(stackID)[0]

        self.logger.debug('Custom Resource Stack created, status = %s' % stack.stack_status)
        return stack

    def deleteStack(self, region, stackID):
        self.logger.debug('Deleting the Custom Resource stack')
        conn = boto.cloudformation.connect_to_region(region)
        conn.delete_stack(stackID)

    def doTest(self, region):
        # create custom resource stack
        stack = self.createCustomResource(region)

        # retrieve topic ARN in output
        with open ("cfn/amifinder_test.template.json", "r") as cfnTemplateFile:
            testTemplateRaw=cfnTemplateFile.read()
        topicARN = {'topic_arn' :  stack.outputs[0].value }
        testTemplate = pystache.render(testTemplateRaw, topicARN)

        # launch sample template stack
        conn = boto.cloudformation.connect_to_region(region)
        now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
        stackID = conn.create_stack(stack_name='TestAMIFinderCustomResource-' + now, template_body=testTemplate)
        stackTest = conn.describe_stacks(stackID)[0]
        print vars(stackTest)
        self.logger.debug('Waiting for Test Stack to be created')
        while stackTest.stack_status == 'CREATE_IN_PROGRESS':
            self.logger.debug('.')
            time.sleep(10)
            stackTest = conn.describe_stacks(stackID)[0]
        self.logger.debug('Test Stack created, status = %s' % stackTest.stack_status)

        # delete custom resource stack
        self.deleteStack(region, stack.stack_id)
        self.deleteStack(region, stackTest.stack_id)

        return stackTest

    def test_eu_west_1(self):
        region = 'eu-west-1'
        stack = self.doTest(region)
        self.assertEqual(len(stack.outputs), 1, "Test Stack outputs len is not 1")
        self.assertRegexpMatches( stack.outputs[0].value, '^ami-.*$',"Test Stack does not return an AMI id")

if __name__ == '__main__':
    unittest.main()