"""Its very important to install in virtualenv
pip install WebTest
pip install PyYaml"""
import unittest
import webtest
import search_algorithm
import json
from google.appengine.ext import testbed
from google.appengine.api import search


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(search_algorithm.application)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def testEmpty_AlgorithmsHandler(self):
        self.testbed.init_search_stub()
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertEqual('[]', response.normal_body)
        self.assertEqual('application/json', response.content_type)

    def testOneAlgorithm_AlgorithmsHandler(self):
        self.testbed.init_search_stub()
        data={}
        data['algorithmId']='algorithmId1'
        data['algorithmSummary']='algorithmSummary1'
        data['displayName']='displayName1'
        data['linkURL']='linkURL1'
        datalist=[]
        datalist.append(data)
        document = search_algorithm.create_document(datalist[0]['algorithmId'],
                                                    datalist[0]['algorithmSummary'],
                                                    datalist[0]['displayName'],
                                                    datalist[0]['linkURL'])
        search.Index(name=search_algorithm._INDEX_STRING).put(document)
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        #datalist[0]['linkURL'] = u'changedLinkURL'
        self.assertListEqual(datalist,json.loads(response.normal_body))

        #self.assertEqual('[{"algorithmSummary": "algorithmSummary1", "algorithmId": "algorithmId1", "displayName": "displayName1", "linkURL": "linkURL1"}]',
        #                   response.normal_body)
        self.assertEqual('application/json', response.content_type)


if __name__ == '__main__':
    unittest.main()
