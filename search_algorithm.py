"""Api for searching algorithms in App Engine search API."""


from datetime import datetime
from urlparse import urlparse, parse_qs

import webapp2
import json
from google.appengine.api import search
import string

_INDEX_STRING = 'algorithms'


def has_no_whitespaces(my_string):
    for my_char in my_string:
        if my_char in string.whitespace:
            return False
    return True


def is_algorithm_id(x):
    """Checks if its legitimate algorithmId aka <search document>.doc_id"""
    if not isinstance(x, basestring):
        return False
    if len(x) == 0:
        return False
    if not has_no_whitespaces(x):
        # search.document.doc_id can not contain whitespaces in name
        return False
    if x[0] == '!':
        # search.document.doc_id cant begin with '!'
        return False
    return True


def is_algorithm_dict(x):
    """ Checks if dictionary object contains legitimate algorithm data"""
    if not isinstance(x, dict):
        return False
    else:
        if not len(x.keys()) == 4:
            return False
        else:
            for key in ['algorithmId', 'algorithmSummary', 'displayName', 'linkURL']:
                if key not in x.keys():
                    return False
                if not isinstance(x[key], basestring):
                    return False
            if not is_algorithm_id(x['algorithmId']):
                return False
    return True


def del_all(index_object):
    """
    Deletes all algorithms to clear database. No use case. Just to start over for debugging and reiterating while testing.
    <index_object>.get_range() returns max 100 docs so we have iterate to clear it all.
    Batch deleting is quicker and is restricted to 200 > 100 so its easy to iterate in while loop
    :param index_object: 
    :return: 
    """
    while True:
        documents = index_object.get_range(ids_only=True)
        id_s = []
        for document in documents:
            id_s.append(document.doc_id)
        if len(id_s) == 0:
            # break if there are no more documents
            break
        index_object.delete(id_s)


def query_algorithms(index_object, query_string='', sort_options_object=None):
    """
    Queries the Full Text Search database and returns all results
    :param index_object:
    :param query_string:
    :param sort_options_object:
    :rtype: list: list of dictionaries of all fields except date field in all found documents.
    """

    algorithms_list = []

    if query_string == '' and sort_options_object is None:
        start_id = None
        while True:
            results = index_object.get_range(start_id, include_start_object=False)  # returns max 100 rows
            if len(results.results) == 0:
                # break if there are no more documents
                break
            for found_document in results:
                start_id = found_document.doc_id
                algorithm_index_dict = {}
                for field in found_document.fields:
                    if field.name != 'date':
                        algorithm_index_dict[field.name] = field.value
                algorithms_list.append(algorithm_index_dict)
    else:
        cursor = search.Cursor()
        while cursor:
            if sort_options_object:
                query_options = search.QueryOptions(cursor=cursor,
                                                    sort_options=sort_options_object)
            else:
                query_options = search.QueryOptions(cursor=cursor)

            results = index_object.search(search.Query(query_string=query_string, options=query_options))
            cursor = results.cursor
            for found_document in results:
                algorithm_index_dict = {}
                for field in found_document.fields:
                    if field.name != 'date':
                        algorithm_index_dict[field.name] = field.value
                algorithms_list.append(algorithm_index_dict)

    return algorithms_list


def get_algorithm(index_object, algorithm_id):
    """
    Queries the Full Text Search database and returns one docment where id=algorithm_id
    :param index_object:
    :param algorithm_id
    :rtype : dict
    """
    found_document = index_object.get(algorithm_id)
    if found_document is None:
        return 1
    algorithm_index_dict = {}
    for field in found_document.fields:
        if field.name != 'date':
            algorithm_index_dict[field.name] = field.value
    return algorithm_index_dict


def create_document(algorithm_id, algorithm_summary, display_name, link_url):
    """creates a search.Document.
    :param algorithm_id:
    :param algorithm_summary: HTML
    :param display_name:
    :param link_url:
    :rtype : google.appengine.api.search.Document
    """
    return search.Document(doc_id=algorithm_id,
                           fields=[
                               search.TextField(name='algorithmId', value=algorithm_id),
                               search.HtmlField(name='algorithmSummary', value=algorithm_summary),
                               search.TextField(name='displayName', value=display_name),
                               search.TextField(name='linkURL', value=link_url),
                               search.DateField(name='date', value=datetime.now())
                           ])


class AlgorithmsIdHandler(webapp2.RequestHandler):
    def get(self, algorithm_id):
        algorithm = get_algorithm(search.Index(name=_INDEX_STRING), algorithm_id)
        if algorithm != 1:
            json.dump(algorithm, self.response.out)
            self.response.status = 200
        else:
            data = {
                "code": 404,
                "fields": "string",
                "message": "Algorithm Not Found"
            }
            self.response.status = 404
            json.dump(data, self.response.out)
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
        self.response.headers['Content-Type'] = 'application/json'


class AlgorithmsHandler(webapp2.RequestHandler):
    """Main class for requests"""

    def get(self):
        """GET algorithms from Full Text Search"""
        url = urlparse(self.request.uri)
        query_string = ''
        if url.query:
            q = parse_qs(url.query)
            if 'query' in q.keys():
                query_string = q['query'][0]
                algorithms_list = query_algorithms(search.Index(name=_INDEX_STRING), query_string)
                json.dump(algorithms_list, self.response.out)
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json'
                self.response.status = 200
            else:
                data = {
                    "code": 400,
                    "fields": "string",
                    "message": "Malformed Data"
                }
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers',
                                                 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json'
                self.response.status = 400
                json.dump(data, self.response.out)
        else:
            algorithms_list = query_algorithms(search.Index(name=_INDEX_STRING), query_string)
            json.dump(algorithms_list, self.response.out)
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers',
                                             'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json'
            self.response.status = 200

    def post(self):
        """Add a new Algorithm to Full Text Search"""
        if self.request.content_type == 'application/json':
            try:
                data = json.loads(self.request.body)
            except:
                data = {
                    "code": 400,
                    "fields": "string",
                    "message": "Malformed Data"
                }
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers',
                                                 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json'
                self.response.status = 400
                json.dump(data, self.response.out)

            if is_algorithm_dict(data):
                document = create_document(data['algorithmId'],
                                           data['algorithmSummary'],
                                           data['displayName'],
                                           data['linkURL'])
                search.Index(name=_INDEX_STRING).put(document)
                self.response.status = 200
            else:
                data = {
                    "code": 400,
                    "fields": "string",
                    "message": "Malformed Data"
                }
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers',
                                                 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json'
                self.response.status = 400
                json.dump(data, self.response.out)

        else:
            data = {
                "code": 400,
                "fields": "string",
                "message": "Malformed Data"
            }
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json'
            self.response.status = 400
            json.dump(data, self.response.out)

    def delete(self):
        """
        Delete all Algorithms from Full Text Search
        Just to clear database for testing purposes.
        """
        del_all(search.Index(name=_INDEX_STRING))
        self.response.status = 200


def handle_404(request, response, exception):
    """Handles not found error"""
    data = {
        "code": 404,
        "fields": "string",
        "message": "Page Not Found"
    }
    response.headers.add_header("Access-Control-Allow-Origin", "*")
    response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
    response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization, ' +
                                'x-requested-with, Total-Count, Total-Pages, Error-Message')
    response.headers['Content-Type'] = 'application/json'
    response.status = 404
    json.dump(data, response.out)


application = webapp2.WSGIApplication(
    [('/', AlgorithmsHandler), ('/algorithms/(.+)', AlgorithmsIdHandler)],
    debug=True)

application.error_handlers[404] = handle_404
