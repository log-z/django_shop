import json

from django.http import JsonResponse


class APIResultBuilder:

    def __init__(self):
        self.data = {}

    def set_results(self, result):
        self.data['results'] = result
        return self

    def set_errors(self, error):
        self.data['errors'] = error
        return self

    def as_json(self):
        return json.dumps(self.data)

    def as_json_response(self, status=200):
        self.data['status'] = status
        return JsonResponse(self.data)
