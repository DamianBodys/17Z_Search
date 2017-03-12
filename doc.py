#!/usr/bin/env python

import webapp2
from webapp2_extras.routes import RedirectRoute

app = webapp2.WSGIApplication([
    RedirectRoute('/<:.*>', redirect_to='/swaggerui/index.html?url=%2Fswagger.json')
], debug=False)
