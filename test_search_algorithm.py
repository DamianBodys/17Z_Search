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


def create_test_algorithm_list(datalist, length):
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
        wrong_list = []
        right_list = []
        create_test_algorithm_list(wrong_list, 1)
        create_test_algorithm_list(right_list, 1)
        wrong_list[0]['linkURL'] = 'wrongLinkURL'
        document = search_algorithm.create_document(right_list[0]['algorithmId'],
                                                    right_list[0]['algorithmSummary'],
                                                    right_list[0]['displayName'],
                                                    right_list[0]['linkURL'])
        search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertListEqual(right_list, json.loads(response.normal_body))
        self.assertNotIn(wrong_list[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)

    def testTwoAlgorithms_AlgorithmsHandler(self):
        """Tests if only two algorithms are returned from database containing only 2 algorithms"""
        wrong_list = []
        right_list = []
        create_test_algorithm_list(wrong_list, 2)
        create_test_algorithm_list(right_list, 2)
        wrong_list[0]['linkURL'] = 'wrongLinkURL'
        for i in range(2):
            document = search_algorithm.create_document(right_list[i]['algorithmId'],
                                                        right_list[i]['algorithmSummary'],
                                                        right_list[i]['displayName'],
                                                        right_list[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertItemsEqual(right_list, json.loads(response.normal_body))
        self.assertNotIn(wrong_list[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)

    def test100Algorithms_AlgorithmsHandler(self):
        """Tests if 100 algorithms are returned from database containing only 100 algorithms"""
        wrong_list = []
        right_list = []
        create_test_algorithm_list(wrong_list, 1)
        create_test_algorithm_list(right_list, 100)
        wrong_list[0]['linkURL'] = 'wrongLinkURL'
        for i in range(100):
            document = search_algorithm.create_document(right_list[i]['algorithmId'],
                                                        right_list[i]['algorithmSummary'],
                                                        right_list[i]['displayName'],
                                                        right_list[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int, msg='The response was other then 200 OK')
        self.assertItemsEqual(right_list, json.loads(response.normal_body),
                              msg='The list of algorithms is not the same as in database')
        self.assertNotIn(wrong_list[0], json.loads(response.normal_body), 
                         msg='The list of algorithms contains nonexistent data')
        self.assertEqual('application/json', response.content_type, msg='Wrong content type of an answer')

    def test101Algorithms_query_algorithms(self):
        """Tests if 101 algorithms are returned from database containing only 101 algorithms
        It should fail if <index_object>.get_range() is used because it returns only 100 results"""
        right_list = []
        create_test_algorithm_list(right_list, 101)
        documents = []
        for i in range(101):
            document = search_algorithm.create_document(right_list[i]['algorithmId'],
                                                        right_list[i]['algorithmSummary'],
                                                        right_list[i]['displayName'],
                                                        right_list[i]['linkURL'])
            documents.append(document)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        result = search_algorithm.query_algorithms(index)
        self.assertEqual(101, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_list, result, msg='Discrepancy in returned algorithms')

    def test101Algorithms_AlgorithmsHandler(self):
        """Tests if 101 algorithms are returned from database containing only 101 algorithms
        It should fail if <index_object>.get_range() is used because it returns only
         100 results"""
        wrong_list = []
        right_list = []
        create_test_algorithm_list(wrong_list, 1)
        create_test_algorithm_list(right_list, 101)
        wrong_list[0]['linkURL'] = 'wrongLinkURL'
        for i in range(101):
            document = search_algorithm.create_document(right_list[i]['algorithmId'],
                                                        right_list[i]['algorithmSummary'],
                                                        right_list[i]['displayName'],
                                                        right_list[i]['linkURL'])
            search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertItemsEqual(right_list, json.loads(response.normal_body))
        self.assertNotIn(wrong_list[0], json.loads(response.normal_body))
        self.assertEqual('application/json', response.content_type)



if __name__ == '__main__':
    unittest.main()
