from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

from resources import settings


def request_frequency_single_ip(request_frequency, request_counter):
    def request_limit(func):
        def wrapper(*args, **kwargs):
            request = args[-1]
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                client_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                client_ip = request.META['REMOTE_ADDR']

            cache_key = "{}{}".format(client_ip, request.get_full_path())
            counter = cache.get(cache_key)
            if counter and isinstance(counter, int):
                counter += 1
            else:
                counter = 1
            if counter > request_counter and not settings.DEBUG:
                return Response("Request too frequency, please try latter.", status=status.HTTP_403_FORBIDDEN)
            cache.set(cache_key, counter, request_frequency)
            return func(*args, **kwargs)

        return wrapper

    return request_limit
