from django.shortcuts import render

import requests
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
import random
import string
from coupon.models import CouponType, Coupon, CouponRequest, ApiKey
from django.http import HttpResponse, JsonResponse

@csrf_exempt
def couponCreate(request):
    if request.method == 'POST':
        api_key = ''
        coupon_type_id = ''
        coupon_count = ''
        missing_field_name = ''
        success = True

        json_data = json.loads(request.body)
        if 'api_key' in json_data:
            api_key = json_data['api_key']
        else:
            missing_field_name += 'api_key, '
            success = False

        if 'coupon_type' in json_data:
            coupon_type_id = json_data['coupon_type']
        else:
            missing_field_name += 'coupon_type, '
            success = False

        if 'coupon_count' in json_data:
            coupon_count = json_data['coupon_count']
        else:
            missing_field_name += 'coupon_count, '
            success = False

        if not success:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
            })
            response.status_code = 500
            return response

        if coupon_count < 1:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Coupon Count should be greater than 1",
            })
            response.status_code = 500
            return response

        if not existApiKey(api_key):
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid API Key!",
            })
            response.status_code = 500
            return response
        coupon_type_data = existCouponType(coupon_type_id);
        if not coupon_type_data:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid Coupon Type!",
            })
            response.status_code = 500
            return response

        coupon_codes = createCouponData(coupon_count, coupon_type_id, coupon_type_data)
        response = JsonResponse({
            "success": 'true',
            "msg": 'created coupon successfully',
            'coupon_codes': json.dumps(coupon_codes),
            'coupon_count': coupon_count,
            'coupon_issuance_date': datetime.datetime.now()
        })
        response.status_code = 200
        return response
    else:
        response = JsonResponse({
            "success": 'false',
            "error_msg": 'Invalid Request Method!'
        })
        response.status_code = 200
        return response

@csrf_exempt
def couponRedeem(request):
    if request.method == 'POST':
        api_key = ''
        coupon_type_id = ''
        coupon_code = ''
        missing_field_name = ''
        success = True

        json_data = json.loads(request.body)
        if 'api_key' in json_data:
            api_key = json_data['api_key']
        else:
            missing_field_name += 'api_key, '
            success = False

        if 'coupon_type' in json_data:
            coupon_type_id = json_data['coupon_type']
        else:
            missing_field_name += 'coupon_type, '
            success = False

        if 'coupon_code' in json_data:
            coupon_code = json_data['coupon_code']
        else:
            missing_field_name += 'coupon_code, '
            success = False

        if not success:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
            })
            response.status_code = 500
            return response

        if coupon_code == '':
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Coupon Code shouldn't be empty string",
            })
            response.status_code = 500
            return response

        if not existApiKey(api_key):
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid API Key!",
            })
            response.status_code = 500
            return response
        coupon_type_data = existCouponType(coupon_type_id);
        if not coupon_type_data:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid Coupon Type!",
            })
            response.status_code = 500
            return response

        coupon_redeem_result = redeemCouponData(coupon_code, coupon_type_id, coupon_type_data)
        if coupon_redeem_result:
            response = JsonResponse({
                "success": 'true',
                "msg": 'redeemed coupon successfully',
                'coupon_codes': coupon_code,
            })
        else:
            response = JsonResponse({
                "success": 'false',
                "msg": 'not found coupon code',
            })
        response.status_code = 200
        return response
    else:
        response = JsonResponse({
            "success": 'false',
            "error_msg": 'Invalid Request Method!'
        })
        response.status_code = 200
        return response


@csrf_exempt
def couponValidate(request):
    if request.method == 'POST':
        api_key = ''
        coupon_type_id = ''
        coupon_code = ''
        missing_field_name = ''
        success = True

        json_data = json.loads(request.body)
        if 'api_key' in json_data:
            api_key = json_data['api_key']
        else:
            missing_field_name += 'api_key, '
            success = False

        if 'coupon_type' in json_data:
            coupon_type_id = json_data['coupon_type']
        else:
            missing_field_name += 'coupon_type, '
            success = False

        if 'coupon_code' in json_data:
            coupon_code = json_data['coupon_code']
        else:
            missing_field_name += 'coupon_code, '
            success = False

        if not success:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
            })
            response.status_code = 500
            return response

        if coupon_code == '':
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Coupon Code shouldn't be empty string",
            })
            response.status_code = 500
            return response

        if not existApiKey(api_key):
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid API Key!",
            })
            response.status_code = 500
            return response
        coupon_type_data = existCouponType(coupon_type_id);
        if not coupon_type_data:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid Coupon Type!",
            })
            response.status_code = 500
            return response

        coupon_validate_result = validateCouponData(coupon_code, coupon_type_id, coupon_type_data)
        if coupon_validate_result:
            response = JsonResponse({
                "success": 'true',
                "msg": 'validated coupon successfully',
                'coupon_codes': coupon_code,
            })
        else:
            response = JsonResponse({
                "success": 'false',
                "msg": 'not found coupon code',
            })
        response.status_code = 200
        return response
    else:
        response = JsonResponse({
            "success": 'false',
            "error_msg": 'Invalid Request Method!'
        })
        response.status_code = 200
        return response

@csrf_exempt
def couponActivate(request):
    if request.method == 'POST':
        api_key = ''
        coupon_type_id = ''
        coupon_code = ''
        missing_field_name = ''
        success = True

        json_data = json.loads(request.body)
        if 'api_key' in json_data:
            api_key = json_data['api_key']
        else:
            missing_field_name += 'api_key, '
            success = False

        if 'coupon_type' in json_data:
            coupon_type_id = json_data['coupon_type']
        else:
            missing_field_name += 'coupon_type, '
            success = False

        if 'coupon_code' in json_data:
            coupon_code = json_data['coupon_code']
        else:
            missing_field_name += 'coupon_code, '
            success = False

        if not success:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
            })
            response.status_code = 500
            return response

        if coupon_code == '':
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Coupon Code shouldn't be empty string",
            })
            response.status_code = 500
            return response

        if not existApiKey(api_key):
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid API Key!",
            })
            response.status_code = 500
            return response
        coupon_type_data = existCouponType(coupon_type_id);
        if not coupon_type_data:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "Invalid Coupon Type!",
            })
            response.status_code = 500
            return response

        coupon_activate_result = activateCouponData(coupon_code, coupon_type_id, coupon_type_data)
        if coupon_activate_result:
            response = JsonResponse({
                "success": 'true',
                "msg": 'activated coupon successfully',
                'coupon_codes': coupon_code,
            })
        else:
            response = JsonResponse({
                "success": 'false',
                "msg": 'not found coupon code',
            })
        response.status_code = 200
        return response
    else:
        response = JsonResponse({
            "success": 'false',
            "error_msg": 'Invalid Request Method!'
        })
        response.status_code = 200
        return response

def existApiKey(api_key):
    keys = ApiKey.objects.filter(api_key=api_key)
    if keys.count() >= 1:
        return True
    else:
        return False

def existCouponType(coupon_type):
    coupon_types = CouponType.objects.filter(coupon_id=coupon_type)
    if coupon_types.count() >= 1:
        return coupon_types[0]
    else:
        return False


def createCouponData(coupon_count, coupon_type, coupon_type_data):
    coupon_code_list = []
    coupon_return_code_list = []
    coupon_issuance_date = datetime.datetime.now()
    coupon_expiration_date = datetime.datetime.now() + datetime.timedelta(coupon_type_data.coupon_validity_days)
    for i in range(1, coupon_count):
        coupon_code = generateCoupon()
        coupon_code_list.append(coupon_code)
        coupon = Coupon(coupon=coupon_code)
        coupon.save()
        return_coupon_code = coupon_type_data.prefix + coupon_code + coupon_type_data.suffix
        coupon_return_code_list.append(return_coupon_code)
    coupon_code_json = json.dumps(coupon_code_list)
    coupon_request = CouponRequest(coupon_type_id=coupon_type, coupon_count=coupon_count, coupon_code=coupon_code_json,
                    coupon_issuance_date=coupon_issuance_date, coupon_expiration_date=coupon_expiration_date)
    coupon_request.save()
    return coupon_return_code_list

def generateCoupon():
    return ''.join([random.choice(string.ascii_uppercase + string.digits) for n in range(16)])



def redeemCouponData(coupon_code, coupon_type, coupon_type_data):
    try:
        coupon = Coupon.objects.get(coupon=coupon_code)
    except Coupon.DoesNotExist:
        return False
    coupon.redeemed = 'True'
    coupon.save()
    return True

def validateCouponData(coupon_code, coupon_type, coupon_type_data):
    try:
        coupon = Coupon.objects.get(coupon=coupon_code)
    except Coupon.DoesNotExist:
        return False
    coupon.validated = 'True'
    coupon.save()
    return True

def activateCouponData(coupon_code, coupon_type, coupon_type_data):
    try:
        coupon = Coupon.objects.get(coupon=coupon_code)
    except Coupon.DoesNotExist:
        return False
    coupon.activated = 'True'
    coupon.save()
    return True
