import json

from django.http import JsonResponse


class APIResultBuilder:

    def __init__(self):
        self.data = {}

    def set_result(self, result):
        self.data['result'] = result
        return self

    def set_error(self, error):
        self.data['error'] = error
        return self

    def as_json(self):
        return json.dumps(self.data)

    def as_json_response(self, status):
        return JsonResponse(self.data, status=status)
        # TODO: status_code需要调整到response的json-body中

