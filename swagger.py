import webapp2
import json


class SwaggerHandler(webapp2.RequestHandler):
    def get(self):
        data = json.load(open('static/swagger.json'))
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
        self.response.headers['Content-Type'] = 'application/json'
        json.dump(data, self.response.out)


app = webapp2.WSGIApplication([
    ('/swagger.json', SwaggerHandler)
], debug=True)
