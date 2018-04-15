import webapp2
import search_dataset
import search_algorithm
from common_functions import handle_404


application = webapp2.WSGIApplication(
    [('/algorithms/', search_algorithm.AlgorithmsHandler), ('/algorithms/(.+)', search_algorithm.AlgorithmsIdHandler), ('/datasets/', search_dataset.DatasetsHandler), ('/datasets/(.+)', search_dataset.DatasetsIdHandler)],
    debug=True)

application.error_handlers[404] = handle_404
