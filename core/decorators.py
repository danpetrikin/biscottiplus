from functools import wraps
from django.http import HttpResponse
from django.utils import simplejson

def jsonify(func):
    @wraps(func)
    def jsonify_wrapper(request, **kwargs):
        try:
            ret_value = func(request, **kwargs)
            if isinstance(ret_value, HttpResponse):
                return ret_value

            http_status = 200
            if 'http_status' in ret_value:
                http_status = ret_value.pop('http_status')
        except Exception, err:
            return HttpResponse(simplejson.dumps({'success': False,
                                                  'message': 'Unexpected error'}),
                                status=500)

        return HttpResponse(simplejson.dumps(ret_value), status=http_status, mimetype='application/json')
    return jsonify_wrapper
