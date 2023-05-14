from django.http import HttpRequest
from datetime import datetime
from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):
    print("initial_call")

    def middleware(request: HttpRequest):
        print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response
    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print("requests count", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("responses count", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("Got", self.exceptions_count, "exception so far")


class ThrottlingIPMiddleware:
    users_dict = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        ip = self.get_client_ip(request)
        if self.users_dict.get(ip) is None:
            response = self.get_response(request)
            self.users_dict[ip] = datetime.now()
            return response
        else:
            current_time = datetime.now()
            diff_time = current_time.minute - self.users_dict.get(ip).minute
            if diff_time > 0:
                response = self.get_response(request)
                self.users_dict[ip] = datetime.now()
                return response
            else:
                context = {
                    "throttling": "Too much requests. Please, try later."
                }
                return render(request, "requestdataapp/base.html", context=context)

    @classmethod
    def get_client_ip(cls, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
