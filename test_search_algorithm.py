import unittest
import webtest
import search_algorithm
from google.appengine.ext import testbed


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(search_algorithm.application)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def testAlgorithmsHandler(self):
        self.testbed.init_search_stub()
        response = self.testapp.get('/')
        self.assertEqual(200, response.status_int)
        self.assertEqual('[]', response.normal_body)
        self.assertEqual('application/json', response.content_type)


if __name__ == '__main__':
    unittest.main()
