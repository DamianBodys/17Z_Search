import string
import json

def has_no_whitespaces(my_string):
    for my_char in my_string:
        if my_char in string.whitespace:
            return False
    return True


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
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status = 404
    json.dump(data, response.out)