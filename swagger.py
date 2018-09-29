import webapp2
import json
import os


def get_search_url():
    return 'https://zsearch1.appspot.com'
#   if os.environ.get('CLOUD_SHELL').startswith('true'):
 #       return 'https://' + os.environ.get('GOOGLE_CLOUD_PROJECT') +
  #  else:
   #     return 'http://localhost:8080'


class SwaggerHandler(webapp2.RequestHandler):
    def get(self):
        data = json.load(open('static/swagger.json'))
        # changing schemes and host in swagger.json to get_search_url()
        url = get_search_url()
        data['host'] = url.split('://')[1]
        del data['schemes'][:]
        data['schemes'].append(url.split('://')[0])
        # js = json.dumps(data)
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
        self.response.headers['Content-Type'] = 'application/json'
        json.dump(data, self.response.out)


app = webapp2.WSGIApplication([
    ('/swagger.json', SwaggerHandler)
], debug=True)
