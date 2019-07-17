from django.shortcuts import render

import requests
from django.views.decorators.csrf import csrf_exempt
import datetime
from healthcheck.models import HealthCheck
from django.http import HttpResponse, JsonResponse
# Create your views here.

@csrf_exempt
def saveHealthAPI(request):
    requested_api = ''
    if request.method == 'GET' and 'api' in request.GET:
        requested_api = request.GET['api']
    healthcheck = HealthCheck(requested_api=requested_api, requested_time=datetime.datetime.now(), ip_address=get_client_ip(request))
    healthcheck.save()
    response = JsonResponse({
        "success": 'true',
        "requested_api": requested_api,
        "requested_time": datetime.datetime.now(),
        "ip_address": get_client_ip(request)
    })
    response.status_code = 404
    return response

def saveHealth(requested_api, requested_time, ip_address):
    healthcheck = HealthCheck(requested_api=requested_api, requested_time=requested_time, ip_address=ip_address)
    healthcheck.save()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


