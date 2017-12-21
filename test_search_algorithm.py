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
from datetime import datetime


def create_test_algorithm_list(data_list, length):
    """Prepare test data as list by name data_list given by reference
     of length algorithm descriptions"""
    for i in range(length):
        data={}
        data['algorithmId'] = 'algorithmId' + str(i)
        data['algorithmSummary'] = 'algorithmSummary' + str(i)
        data['displayName'] = 'displayName' + str(i)
        data['linkURL'] = 'linkURL' + str(i)
        data_list.append(data)


def create_test_documents_list(data_list, documents, length):
    """ Prepare test documents"""
    for i in range(length):
        document = search.Document(doc_id=data_list[i]['algorithmId'],
                                   fields=[
                                        search.TextField(name='algorithmId', value=data_list[i]['algorithmId']),
                                        search.HtmlField(name='algorithmSummary', value=data_list[i]['algorithmSummary']),
                                        search.TextField(name='displayName', value=data_list[i]['displayName']),
                                        search.TextField(name='linkURL', value=data_list[i]['linkURL']),
                                        search.DateField(name='date', value=datetime.now())
                                   ])
        documents.append(document)


class SearchTestCaseErrorHandlers(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(search_algorithm.application)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def test_error_handler_PageNotFound404(self):
        """
        Tests if 404 is returned if there is no such page/route
        """
        response = self.testapp.get('/notexistentpage/', expect_errors=True)
        self.assertEqual(404, response.status_int)
        self.assertIn('Page Not Found', response.normal_body)
        self.assertEqual('application/json', response.content_type)


class SearchTestCaseAlgorithmsHandler(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(search_algorithm.application)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_AlgorithmsHandler_GETEmpty(self):
        """
        Tests if empty database is returned
        """
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertEqual('[]', response.normal_body)
        self.assertEqual('application/json', response.content_type)

    def test_AlgorithmsHandler_GETMalformedQuery(self):
        """
        Tests if 400 is returned if there is no query= in uri while there is "?" after "/" indicating there are paramete-
        rs to be expected
        """
        response = self.testapp.get('/?qqry=algorithm', expect_errors=True)
        self.assertEqual(400, response.status_int)
        self.assertIn('Malformed Data', response.normal_body)
        self.assertEqual('application/json', response.content_type)

    def test_AlgorithmsHandler_GETOneAlgorithm(self):
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

    def test_AlgorithmsHandler_GETTwoAlgorithms(self):
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

    def test_AlgorithmsHandler_GET100Algorithms(self):
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

    def test_AlgorithmsHandler_GET101Algorithms(self):
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

    def test_AlgorithmsHandler_GET200queryAlgorithms(self):
        """Tests if 200 algorithms are returned from database containing only 200 algorithms by query of string
        algorithms which will be is present in every test algorithm in field displayName == 'algorithm <id>'
        """
        query_string = 'algorithm'
        right_list = []
        create_test_algorithm_list(right_list, 200)
        # changing the right_list to contain string query_string separated from <number> in every displayName field
        # so that the query will return every row in database
        for algorithm in right_list:
            algorithm['displayName'] = query_string + ' ' + algorithm['displayName'].split('displayName')[1]
        documents = []
        create_test_documents_list(right_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        # End of data preparation
        response = self.testapp.get('/?query=' + query_string)
        result = json.loads(response.normal_body)
        self.assertEqual(200, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_list, result, msg='Discrepancy in returned algorithms')

    def test_AlgorithmsHandler_GET1queryfrom200Algorithms(self):
        """Tests if 1 algorithm with query string is returned from database containing 200 algorithms
         by query of string 'displayName102'
        """
        query_string = 'displayName102'
        upload_data_list = []
        create_test_algorithm_list(upload_data_list, 200)
        documents = []
        create_test_documents_list(upload_data_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        # end of data preparation
        number = query_string.split('displayName')[1]
        data = {}
        data['algorithmId'] = 'algorithmId' + number
        data['algorithmSummary'] = 'algorithmSummary' + number
        data['displayName'] = 'displayName' + number
        data['linkURL'] = 'linkURL' + number
        right_answer_list = [data]
        # end right answer list preparation
        response = self.testapp.get('/?query=' + query_string)
        result = json.loads(response.normal_body)
        self.assertEqual(1, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_answer_list, result, msg='Discrepancy in returned algorithms')

    def test_AlgorithmsHandler_GETORqueryfrom200Algorithms(self):
        """Tests if 2 algorithms with query string are returned from database containing only 200 algorithms
         by query of string 'displayName102 OR algorithmId23'
        """
        query_string = 'displayName102 OR algorithmId23'
        upload_data_list = []
        create_test_algorithm_list(upload_data_list, 200)
        documents = []
        create_test_documents_list(upload_data_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        # end of data preparation
        numbers = ['23', '102']
        right_answer_list = []
        for number in numbers:
            data = {}
            data['algorithmId'] = 'algorithmId' + number
            data['algorithmSummary'] = 'algorithmSummary' + number
            data['displayName'] = 'displayName' + number
            data['linkURL'] = 'linkURL' + number
            right_answer_list.append(data)
        # end right answer list preparation
        response = self.testapp.get('/?query=' + query_string)
        result = json.loads(response.normal_body)
        self.assertEqual(len(right_answer_list), len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_answer_list, result, msg='Discrepancy in returned algorithms')

    def test_AlgorithmsHandler_POST(self):
        data={}
        data['algorithmId'] = 'aId'
        data['algorithmSummary'] = 'aSummary'
        data['displayName'] = 'dName'
        data['linkURL'] = 'lURL'
        input_json = json.dumps(data)
        response = self.testapp.post('/', params=input_json, content_type='application/json')
        self.assertEqual(200, response.status_int, msg='Wrong answer code')
        # get data from search
        index = search.Index(name=search_algorithm._INDEX_STRING)
        test_document = index.get('aId')
        self.assertIsNotNone(test_document, msg='The posted document doc_id is not found in search database')
        self.assertEqual('aId', test_document.doc_id)
        self.assertEqual('aId', test_document.field('algorithmId').value)
        self.assertEqual('aSummary', test_document.field('algorithmSummary').value)
        self.assertEqual('dName', test_document.field('displayName').value)
        self.assertEqual('lURL', test_document.field('linkURL').value)
        self.assertGreater(datetime.now(), test_document.field('date').value)

    def test_AlgorithmsHandler_POSTError400WrongContentType(self):
        data={}
        data['algorithmId'] = 'aId'
        data['algorithmSummary'] = 'aSummary'
        data['displayName'] = 'dName'
        data['linkURL'] = 'lURL'
        input_json = json.dumps(data)
        response = self.testapp.post('/', params=input_json, content_type='text/html', expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong answer code')
        self.assertEqual('application/json', response.content_type)
        self.assertIn('Malformed Data', response.normal_body)

    def test_AlgorithmsHandler_POSTError400WrongData(self):
        data={}
        data['algorithmId'] = 'a' + ' ' + 'Id'
        data['algorithmSummary'] = 'aSummary'
        data['displayName'] = 'dName'
        data['linkURL'] = 'lURL'
        input_json = json.dumps(data)
        response = self.testapp.post('/', params=input_json, content_type='application/json', expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong answer code')
        self.assertEqual('application/json', response.content_type)
        self.assertIn('Malformed Data', response.normal_body)

    def test_AlgorithmsHandler_POSTError400NoBody(self):
        response = self.testapp.post('/', content_type='application/json', expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong answer code')
        self.assertEqual('application/json', response.content_type)
        self.assertIn('Malformed Data', response.normal_body)


class SearchTestCaseUnittest(unittest.TestCase):
    """ Test Case for unittests without webtest"""
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_has_no_whitespaces(self):
        stringOK = 'stringOK'
        stringNOK = stringOK + '\n'
        self.assertTrue(search_algorithm.has_no_whitespaces(stringOK), msg='There ware whitespaces detected in legitimate string')
        self.assertFalse(search_algorithm.has_no_whitespaces(stringNOK), msg='The whitespace was not detected in string with whitespaces')

    def test_is_algorithm_dict_legitimate(self):
        data={}
        data['algorithmId'] = 'aId'
        data['algorithmSummary'] = 'aSummary'
        data['displayName'] = 'dName'
        data['linkURL'] = 'lURL'
        self.assertTrue(search_algorithm.is_algorithm_dict(data), msg='Legitimate Algorithm is detected as no good')

    def test_is_algorithm_dict_Error(self):
        data = {}
        data['algorithmId'] = 'a' + ' ' + 'Id'
        data['algorithmSummary'] = 'aSummary'
        data['displayName'] = 'dName'
        data['linkURL'] = 'lURL'
        self.assertFalse(search_algorithm.is_algorithm_dict(data), msg='Wrong Algorithm is detected as good')

    def test_query_algorithms_101Algorithms_(self):
        """Tests if 101 algorithms without query string are returned from database containing only 101 algorithms
        It should fail if <index_object>.get_range() is used because it returns only 100 results"""
        right_list = []
        create_test_algorithm_list(right_list, 101)
        documents = []
        create_test_documents_list(right_list, documents, 101)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        result = search_algorithm.query_algorithms(index)
        self.assertEqual(101, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_list, result, msg='Discrepancy in returned algorithms')

    def test_query_algorithms_200queryAlgorithms(self):
        """Tests if 200 algorithms with query string are returned from database containing only 200 algorithms by query of string
        algorithms which will be is present in every test algorithm in field displayName == 'algorithm <id>'
        """
        query_string = 'algorithm'
        right_list = []
        create_test_algorithm_list(right_list, 200)
        # changing right list to contain string 'algorithm' separated from <number> in every displayName field
        for algorithm in right_list:
            algorithm['displayName'] = 'algorithm ' + algorithm['displayName'].split('displayName')[1]
        documents = []
        create_test_documents_list(right_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        result = search_algorithm.query_algorithms(index, query_string)
        self.assertEqual(200, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_list, result, msg='Discrepancy in returned algorithms')

    def test_query_algorithms_1queryfrom200Algorithms(self):
        """Tests if 1 algorithm with query string is returned from database containing only 200 algorithms
         by query of string 'displayName102'
        """
        query_string = 'displayName102'
        upload_data_list = []
        create_test_algorithm_list(upload_data_list, 200)
        documents = []
        create_test_documents_list(upload_data_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        # end of data preparation
        number = query_string.split('displayName')[1]
        data = {}
        data['algorithmId'] = 'algorithmId' + number
        data['algorithmSummary'] = 'algorithmSummary' + number
        data['displayName'] = 'displayName' + number
        data['linkURL'] = 'linkURL' + number
        right_answer_list= [data]
        # end right answer list preparation
        result = search_algorithm.query_algorithms(index, query_string)
        self.assertEqual(1, len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_answer_list, result, msg='Discrepancy in returned algorithms')

    def test_query_algorithms_ORqueryfrom200Algorithms(self):
        """Tests if 2 algorithms with query string are returned from database containing only 200 algorithms
         by query of string 'displayName102 OR algorithmId23'
        """
        query_string = 'displayName102 OR algorithmId23'
        upload_data_list = []
        create_test_algorithm_list(upload_data_list, 200)
        documents = []
        create_test_documents_list(upload_data_list, documents, 200)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        # end of data preparation
        numbers = ['23', '102']
        right_answer_list = []
        for number in numbers:
            data = {}
            data['algorithmId'] = 'algorithmId' + number
            data['algorithmSummary'] = 'algorithmSummary' + number
            data['displayName'] = 'displayName' + number
            data['linkURL'] = 'linkURL' + number
            right_answer_list.append(data)
        # end right answer list preparation
        result = search_algorithm.query_algorithms(index, query_string)
        self.assertEqual(len(right_answer_list), len(result), msg='Wrong number of algorithms')
        self.assertItemsEqual(right_answer_list, result, msg='Discrepancy in returned algorithms')

    def test_create_document(self):
        """ Checks proper creation of google.appengine.api.search.Document"""
        algorithm_id = 'alid'
        algorithm_summary = 'alsum'
        display_name = 'dname'
        link_url = 'lnk'
        test_document = search_algorithm.create_document(algorithm_id, algorithm_summary, display_name, link_url)
        self.assertEqual(algorithm_id, test_document.doc_id)
        self.assertEqual(algorithm_id, test_document.field('algorithmId').value)
        self.assertEqual(algorithm_summary, test_document.field('algorithmSummary').value)
        self.assertEqual(display_name, test_document.field('displayName').value)
        self.assertEqual(link_url, test_document.field('linkURL').value)
        self.assertGreater(datetime.now(), test_document.field('date').value)

    def test_del_all_from101algorithms(self):
        """Tests if all algorithms are deleted from database containing 101 algorithms
        101 is significant because <search index>.get_range gets only 100 records"""
        my_list = []
        create_test_algorithm_list(my_list, 101)
        documents = []
        create_test_documents_list(my_list, documents, 101)
        index = search.Index(name=search_algorithm._INDEX_STRING)
        index.put(documents)
        result = index.get_range()
        self.assertLess(0, len(result.results), msg='There ware no algorithms present before del_all')
        search_algorithm.del_all(index)
        result = index.get_range()
        self.assertEqual(0, len(result.results), msg='There ware algorithms present after del_all')

if __name__ == '__main__':
    unittest.main()
