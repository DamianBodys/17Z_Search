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
import doc
from google.appengine.ext import testbed

class DocTestCase(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(doc.app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def test_redirect_to_swagger(self):
        """
        Tests if 301 is returned
        """
        response = self.testapp.get('/doc')
        self.assertEqual(301, response.status_int)
        self.assertIn('/swaggerui/index.html?url=%2Fswagger.json', response.location)


if __name__ == '__main__':
    unittest.main()
