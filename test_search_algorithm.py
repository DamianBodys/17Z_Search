"""It's very important to install in virtualenv
pip install WebTest
also either insert google_appengine, webapp jinja and yaml libraries in PyCharm library script
according to this https://www.enkisoftware.com/devlogpost-20141231-1-Python_Google_App_Engine_debugging_with_PyCharm_CE
or uncomment lines below
import sys
sys.path.insert(1, '/root/Downloads/google-cloud-sdk/platform/google_appengine')
sys.path.insert(1, '/root/Downloads/google-cloud-sdk/platform/google_appengine/lib/webapp2-2.5.2')
sys.path.insert(1, '/root/Downloads/google-cloud-sdk/platform/google_appengine/lib/jinja2-2.6')
sys.path.insert(1, '/root/Downloads/google-cloud-sdk/platform/google_appengine/lib/yaml/lib')
"""
import unittest
import webtest
import search_algorithm
import json
from google.appengine.ext import testbed
from google.appengine.api import search


def createTestAlgorithmList(datalist, length):
    """Prepare test data as list by name datalist given by reference
     of length algorithm descriptions"""
    for i in range(length):
        data={}
        data['algorithmId'] = 'algorithmId' + str(i)
        data['algorithmSummary'] = 'algorithmSummary' + str(i)
        data['displayName'] = 'displayName' + str(i)
        data['linkURL'] = 'linkURL' + str(i)
        datalist.append(data)


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(search_algorithm.application)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testEmpty_AlgorithmsHandler(self):
        """
        Tests if empty database is returned
        """
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertEqual('[]', response.normal_body)
        self.assertEqual('application/json', response.content_type)

    def testOneAlgorithm_AlgorithmsHandler(self):
        """Tests if only one algorithm is returned from database containing only one algorithm"""
        wronglist = []
        rightlist = []
        createTestAlgorithmList(wronglist, 1)
        createTestAlgorithmList(rightlist, 1)
        wronglist[0]['linkURL'] = 'wrongLinkURL'
        document = search_algorithm.create_document(rightlist[0]['algorithmId'],
                                                    rightlist[0]['algorithmSummary'],
                                                    rightlist[0]['displayName'],
                                                    rightlist[0]['linkURL'])
        search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertListEqual(rightlist, json.loads(response.normal_body))
        self.assertNotIn(wronglist[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)

    def testTwoAlgorithms_AlgorithmsHandler(self):
        """Tests if only two algorithms are returned from database containing only 2 algorithms"""
        wronglist = []
        rightlist = []
        createTestAlgorithmList(wronglist, 2)
        createTestAlgorithmList(rightlist, 2)
        wronglist[0]['linkURL'] = 'wrongLinkURL'
        for i in range(2):
            document = search_algorithm.create_document(rightlist[i]['algorithmId'],
                                                        rightlist[i]['algorithmSummary'],
                                                        rightlist[i]['displayName'],
                                                        rightlist[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertItemsEqual(rightlist, json.loads(response.normal_body))
        self.assertNotIn(wronglist[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)

    def test100Algorithms_AlgorithmsHandler(self):
        """Tests if 100 algorithms are returned from database containing only 100 algorithms"""
        wronglist = []
        rightlist = []
        createTestAlgorithmList(wronglist, 1)
        createTestAlgorithmList(rightlist, 100)
        wronglist[0]['linkURL'] = 'wrongLinkURL'
        for i in range(100):
            document = search_algorithm.create_document(rightlist[i]['algorithmId'],
                                                        rightlist[i]['algorithmSummary'],
                                                        rightlist[i]['displayName'],
                                                        rightlist[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertItemsEqual(rightlist, json.loads(response.normal_body))
        self.assertNotIn(wronglist[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)

    def test101Algorithms_AlgorithmsHandler(self):
        """Tests if 101 algorithms are returned from database containing only 101 algorithms
        It should fail if <index_object>.get_range() is used because it returns only 100 results"""
        wronglist = []
        rightlist = []
        createTestAlgorithmList(wronglist, 1)
        createTestAlgorithmList(rightlist, 101)
        wronglist[0]['linkURL'] = 'wrongLinkURL'
        for i in range(101):
            document = search_algorithm.create_document(rightlist[i]['algorithmId'],
                                                        rightlist[i]['algorithmSummary'],
                                                        rightlist[i]['displayName'],
                                                        rightlist[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        print response.normal_body
        self.assertItemsEqual(rightlist, json.loads(response.normal_body))
        self.assertNotIn(wronglist[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)



if __name__ == '__main__':
    unittest.main()
