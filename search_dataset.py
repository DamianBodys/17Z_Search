from datetime import datetime
from urlparse import urlparse, parse_qs

from common_functions import has_no_whitespaces
import webapp2
import json
from google.appengine.api import search

_INDEX_STRING = 'datasets'

def is_dataset_id(x):
    """Checks if its legitimate datasetId aka <search document>.doc_id"""
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


def is_dataset_dict(x):
    """ Checks if dictionary object contains legitimate dataset data"""
    if not isinstance(x, dict):
        return False
    else:
        if not len(x.keys()) == 4:
            return False
        else:
            for key in ['datasetId', 'datasetSummary', 'displayName', 'linkURL']:
                if key not in x.keys():
                    return False
                if not isinstance(x[key], basestring):
                    return False
            if not is_dataset_id(x['datasetId']):
                return False
    return True

def query_datasets(index_object, query_string='', sort_options_object=None):
    """
    Queries the Full Text Search database and returns all results
    :param index_object:
    :param query_string:
    :param sort_options_object:
    :rtype: list: list of dictionaries of all fields except date field in all found documents.
    """

    datasets_list = []

    if query_string == '' and sort_options_object is None:
        start_id = None
        while True:
            results = index_object.get_range(start_id, include_start_object=False)  # returns max 100 rows
            if len(results.results) == 0:
                # break if there are no more documents
                break
            for found_document in results:
                start_id = found_document.doc_id
                dataset_index_dict = {}
                for field in found_document.fields:
                    if field.name != 'date':
                        dataset_index_dict[field.name] = field.value
                datasets_list.append(dataset_index_dict)
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
                dataset_index_dict = {}
                for field in found_document.fields:
                    if field.name != 'date':
                        dataset_index_dict[field.name] = field.value
                datasets_list.append(dataset_index_dict)

    return datasets_list


def get_dataset(index_object, dataset_id):
    """
    Queries the Full Text Search database and returns one document where id=dataset_id
    :param index_object:
    :param dataset_id
    :rtype : dict
    """
    found_document = index_object.get(dataset_id)
    if found_document is None:
        return 1
    dataset_index_dict = {}
    for field in found_document.fields:
        if field.name != 'date':
            dataset_index_dict[field.name] = field.value
    return dataset_index_dict


def del_dataset(index_object, dataset_id):
    """
    Deletes a dataset
    :param index_object:
    :param dataset_id
    :rtype : int
    """
    found_before = index_object.get(dataset_id)
    if found_before is None:
        return 2
    else:
        index_object.delete(dataset_id)
    found_after = index_object.get(dataset_id)
    if found_after is not None:
        return 1
    return 0


def create_dataset_document(dataset_id, dataset_summary, display_name, link_url):
    """creates a search.Document.
    :param dataset_id:
    :param dataset_summary: HTML
    :param display_name:
    :param link_url:
    :rtype : google.appengine.api.search.Document
    """
    return search.Document(doc_id=dataset_id,
                           fields=[
                               search.TextField(name='datasetId', value=dataset_id),
                               search.HtmlField(name='datasetSummary', value=dataset_summary),
                               search.TextField(name='displayName', value=display_name),
                               search.TextField(name='linkURL', value=link_url),
                               search.DateField(name='date', value=datetime.now())
                           ])


class DatasetsIdHandler(webapp2.RequestHandler):
    def get(self, dataset_id):
        if is_dataset_id(dataset_id):
            dataset = get_dataset(search.Index(name=_INDEX_STRING), dataset_id)
            if dataset != 1:
                json.dump(dataset, self.response.out)
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers',
                                                 'Content-Type, api_key, Authorization,' +
                                                 ' x-requested-with, Total-Count, Total-Pages, Error-Message')
                self.response.status = 200
            else:
                data = {
                    "code": 404,
                    "fields": "string",
                    "message": "Dataset Not Found"
                }
                self.response.status = 404
                json.dump(data, self.response.out)
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization,' +
                                             ' x-requested-with, Total-Count, Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        else:
            data = {
                "code": 400,
                "fields": "string",
                "message": "Malformed Data"
            }
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers',
                                             'Content-Type, api_key, Authorization, x-requested-with, Total-Count,' +
                                             ' Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            self.response.status = 400
            json.dump(data, self.response.out)

    def delete(self, dataset_id):
        if is_dataset_id(dataset_id):
            result = del_dataset(search.Index(name=_INDEX_STRING), dataset_id)
            if result != 1:
                # delete is successful even if the dataset_id was not there
                self.response.status = 200
            else:
                data = {
                    "code": 500,
                    "fields": "string",
                    "message": "Dataset Not Deleted"
                }
                self.response.status = 500
                json.dump(data, self.response.out)
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization,' +
                                             ' x-requested-with, Total-Count, Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        else:
            data = {
                "code": 400,
                "fields": "string",
                "message": "Malformed Data"
            }
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers',
                                             'Content-Type, api_key, Authorization, x-requested-with, Total-Count,' +
                                             ' Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            self.response.status = 400
            json.dump(data, self.response.out)


class DatasetsHandler(webapp2.RequestHandler):
    """Main class for requests"""

    def get(self):
        """GET datasets from Full Text Search"""
        url = urlparse(self.request.uri)
        query_string = ''
        if url.query:
            q = parse_qs(url.query)
            if 'query' in q.keys():
                query_string = q['query'][0]
                datasets_list = query_datasets(search.Index(name=_INDEX_STRING), query_string)
                json.dump(datasets_list, self.response.out)
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
                self.response.headers.add_header('Access-Control-Allow-Headers',
                                                 'Content-Type, api_key, Authorization, x-requested-with, ' +
                                                 'Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
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
                                                 'Content-Type, api_key, Authorization, x-requested-with, ' +
                                                 'Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                self.response.status = 400
                json.dump(data, self.response.out)
        else:
            datasets_list = query_datasets(search.Index(name=_INDEX_STRING), query_string)
            json.dump(datasets_list, self.response.out)
            self.response.headers.add_header("Access-Control-Allow-Origin", "*")
            self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
            self.response.headers.add_header('Access-Control-Allow-Headers',
                                             'Content-Type, api_key, Authorization, x-requested-with, Total-Count,' +
                                             ' Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            self.response.status = 200

    def post(self):
        """Add a new Dataset to Full Text Search"""
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
                                                 'Content-Type, api_key, Authorization, x-requested-with, ' +
                                                 'Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
                self.response.status = 400
                json.dump(data, self.response.out)

            if is_dataset_dict(data):
                document = create_dataset_document(data['datasetId'],
                                           data['datasetSummary'],
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
                                                 'Content-Type, api_key, Authorization, x-requested-with, ' +
                                                 'Total-Count, Total-Pages, Error-Message')
                self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
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
            self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization,' +
                                             ' x-requested-with, Total-Count, Total-Pages, Error-Message')
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            self.response.status = 400
            json.dump(data, self.response.out)

    def delete(self):
        """
        Delete all Datasets from Full Text Search
        Just to clear database for testing purposes.
        """
        del_dataset(search.Index(name=_INDEX_STRING))
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization,' +
                                         ' x-requested-with, Total-Count, Total-Pages, Error-Message')
        self.response.status = 200
