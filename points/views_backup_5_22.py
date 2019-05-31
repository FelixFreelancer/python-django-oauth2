from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# pip install mysql-connector-python
import mysql.connector
import datetime
import json

# import Point Model
from points.models import Point
from simulation.models import Simulation
# Create your views here.
USRENAME = 'root'
PASSWORD = ''
DATABASE = 'notification_proxy'


@csrf_exempt
def pointsAdd(request):
    if request.method == 'POST':
        success = True
        missing_field_name = ''
        third_party_sh_name = ''
        params = {}
        request_mode = ''
        third_userid = ''
        userid = ''
        account_name = ''
        add_amount = ''
        transaction_type = ''
        linked_trans_id = ''
        token = ''

        post_balance = 0
        received_json_data = json.loads(request.body)
        if '3rd_party_sh_name' in received_json_data:
            third_party_sh_name = received_json_data['3rd_party_sh_name']
        else:
            missing_field_name += '3rd_party_sh_name, '
            success = False

        if 'request_mode' in received_json_data:
            request_mode = received_json_data['request_mode']
        else:
            missing_field_name += 'request_mode, '
            success = False

        if 'params' in received_json_data:
            params = received_json_data['params']
        else:
            missing_field_name += 'parameters, '
            success = False

        if '3rd_userid' in params:
            third_userid = params['3rd_userid']
        else:
            missing_field_name += '3rd_userid, '
            success = False

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field_name += 'userid, '
            success = False

        if 'account_name' in params:
            account_name = params['account_name']

        if 'add_amount' in params:
            add_amount = params['add_amount']
        else:
            missing_field_name += 'add_amount, '
            success = False

        if 'transaction_type' in params:
            transaction_type = params['transaction_type']
        else:
            missing_field_name += 'transaction_type, '
            success = False

        if 'linked_trans_id' in params:
            linked_trans_id = params['linked_trans_id']

        if 'token' in params:
            token = params['token']
        else:
            missing_field_name += 'token, '
            success = False

        if success == False:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 200
            return response

        if checkIfTokenExist(token):
            id = checkIfRecordExist(third_party_sh_name, third_userid, account_name)
            if not id == False:
                post_balance = sumBalance(id, add_amount)
            else:
                insertNewPoints(third_party_sh_name, third_userid, request_mode, userid, account_name, add_amount,
                                transaction_type, linked_trans_id, token)
                post_balance = int(add_amount)

            response = JsonResponse({
                "success": 'true',
                "error_msg": "",
                "pre_point_balance": add_amount,
                "post_point_balance": post_balance,
                "add_time": datetime.datetime.now(),
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response
        else:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "token is not valid",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response

    response = JsonResponse({
        "success": 'false',
        "error_msg": "no valid parameters",
        "pre_point_balance": "null",
        "post_point_balance": "null",
        "add_time": "null",
        "3rd_trans_num": "",
        "request_mode": "null"
    })
    response.status_code = 404
    return response

def pointsAddFunc(request):
    if request.method == 'POST':
        success = True
        missing_field_name = ''
        third_party_sh_name = ''
        params = {}
        request_mode = ''
        third_userid = ''
        userid = ''
        account_name = ''
        add_amount = ''
        transaction_type = ''
        linked_trans_id = ''
        token = ''

        post_balance = 0
        received_json_data = json.loads(request.body)
        if '3rd_party_sh_name' in received_json_data:
            third_party_sh_name = received_json_data['3rd_party_sh_name']
        else:
            missing_field_name += '3rd_party_sh_name, '
            success = False

        if 'request_mode' in received_json_data:
            request_mode = received_json_data['request_mode']
        else:
            missing_field_name += 'request_mode, '
            success = False

        if 'params' in received_json_data:
            params = received_json_data['params']
        else:
            missing_field_name += 'parameters, '
            success = False

        if '3rd_userid' in params:
            third_userid = params['3rd_userid']
        else:
            missing_field_name += '3rd_userid, '
            success = False

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field_name += 'userid, '
            success = False

        if 'account_name' in params:
            account_name = params['account_name']

        if 'add_amount' in params:
            add_amount = params['add_amount']
        else:
            missing_field_name += 'add_amount, '
            success = False

        if 'transaction_type' in params:
            transaction_type = params['transaction_type']
        else:
            missing_field_name += 'transaction_type, '
            success = False

        if 'linked_trans_id' in params:
            linked_trans_id = params['linked_trans_id']

        if 'token' in params:
            token = params['token']
        else:
            missing_field_name += 'token, '
            success = False

        if success == False:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 200
            return response

        if checkIfTokenExist(token):
            id = checkIfRecordExist(third_party_sh_name, third_userid, account_name)
            if not id == False:
                post_balance = sumBalance(id, add_amount)
            else:
                insertNewPoints(third_party_sh_name, third_userid, request_mode, userid, account_name, add_amount,
                                transaction_type, linked_trans_id, token)
                post_balance = int(add_amount)

            response = JsonResponse({
                "success": 'true',
                "error_msg": "",
                "pre_point_balance": add_amount,
                "post_point_balance": post_balance,
                "add_time": datetime.datetime.now(),
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response
        else:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "token is not valid",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response

    response = JsonResponse({
        "success": 'false',
        "error_msg": "no valid parameters",
        "pre_point_balance": "null",
        "post_point_balance": "null",
        "add_time": "null",
        "3rd_trans_num": "",
        "request_mode": "null"
    })
    response.status_code = 404
    return response
def checkIfTokenExist(token):
    tokens = Simulation.objects.filter(token=token)
    if tokens.count() >= 1:
        return True
    else:
        return False

def checkIfRecordExist(third_party_sh_name, third_userid, account_name):
    points = [];
    if account_name == '':
        points = Point.objects.filter(third_party_sh_name__iexact=third_party_sh_name, third_userid=third_userid)
    else:
        points = Point.objects.filter(third_party_sh_name__iexact=third_party_sh_name, third_userid=third_userid, account_name=account_name)

    if len(points) >= 1:
        return points[0].id
    else:
        return False

def sumBalance(id, add_amount):
    if not add_amount.isdigit():
        add_amount = 0
    points = Point.objects.filter(id=id)
    current_balance = int(points[0].balance) + int(add_amount)
    Point.objects.filter(id=id).update(balance=current_balance)
    return current_balance


def insertNewPoints(third_party_sh_name, third_userid, request_mode, userid, account_name, add_amount, transaction_type,
                    linked_trans_id, token):
    expiration_time = datetime.datetime.now() + datetime.timedelta(30)
    add_point = Point(third_party_sh_name=third_party_sh_name, third_userid=third_userid, request_mode=request_mode,
                      userid=userid, account_name=account_name, balance=add_amount, transaction_type=transaction_type,
                      linked_trans_id=linked_trans_id, expiration_time=expiration_time, token=token)
    add_point.save()


@csrf_exempt
def pointsDeduct(request):
    if request.method == 'POST':
        success = True
        missing_field_name = ''
        third_party_sh_name = ''
        request_mode = ''
        params = {}
        third_userid = ''
        userid = ''
        account_name = ''
        deduct_amount = ''
        transaction_type = ''
        linked_trans_id = ''
        token = ''
        post_balance = 0

        error_msg = ""
        deduct_time = ""
        received_json_data = json.loads(request.body)
        if '3rd_party_sh_name' in received_json_data:
            third_party_sh_name = received_json_data['3rd_party_sh_name']
        else:
            missing_field_name += '3rd_party_sh_name, '
            success = False

        if 'request_mode' in received_json_data:
            request_mode = received_json_data['request_mode']
        else:
            missing_field_name += 'request_mode, '
            success = False

        if 'params' in received_json_data:
            params = received_json_data['params']
        else:
            missing_field_name += 'parameters, '
            success = False

        if '3rd_userid' in params:
            third_userid = params['3rd_userid']
        else:
            missing_field_name += '3rd_userid, '
            success = False

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field_name += 'userid, '
            success = False

        if 'account_name' in params:
            account_name = params['account_name']

        if 'deduct_amount' in params:
            deduct_amount = params['deduct_amount']
        else:
            missing_field_name += 'deduct_amount, '
            success = False

        if 'transaction_type' in params:
            transaction_type = params['transaction_type']
        else:
            missing_field_name += 'transaction_type, '
            success = False

        if 'linked_trans_id' in params:
            linked_trans_id = params['linked_trans_id']

        if 'token' in params:
            token = params['token']
        else:
            missing_field_name += 'token, '
            success = False

        if success == False:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 200
            return response

        if checkIfTokenExist(token):
            id = checkIfRecordExist(third_party_sh_name, third_userid, account_name)
            if not id == False:
                post_balance = deductBalance(id, deduct_amount)
                if post_balance == '':
                    error_msg = "insufficient points balance for deduction operation"
                    post_balance = 'null'
                    deduct_time = 'null'
                else:
                    deduct_time = datetime.datetime.now()
            else:
                error_msg = "not found the record according to these parameters"
                post_balance = 'null'
                deduct_time = 'null'

            response = JsonResponse({
                "success": 'true',
                "error_msg": error_msg,
                "pre_point_balance": deduct_amount,
                "post_point_balance": post_balance,
                "deduct_time": deduct_time,
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response
        else:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "token is not valid",
                "pre_point_balance": "null",
                "post_point_balance": "null",
                "add_time": "null",
                "3rd_trans_num": "",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response

    response = JsonResponse({
        "success": 'false',
        "error_msg": "no valid parameters",
        "pre_point_balance": "null",
        "post_point_balance": "null",
        "add_time": "null",
        "3rd_trans_num": "",
        "request_mode": "null"
    })
    response.status_code = 404
    return response


def deductBalance(id, deduct_amount):
    if not deduct_amount.isdigit():
        deduct_amount = 0
    points = Point.objects.filter(id=id)
    current_balance = int(points[0].balance) - int(deduct_amount)
    if current_balance < 0:
        current_balance = ''
    else:
        Point.objects.filter(id=id).update(balance=current_balance)
    return current_balance

@csrf_exempt
def pointsEnquiry(request):
    if request.method == 'POST':
        success = True
        missing_field_name = ''
        third_party_sh_name = ''
        request_mode = ''
        params = {}
        third_userid = ''
        userid = ''
        account_name = ''
        token = ''
        post_balance = 0

        error_msg = ""
        received_json_data = json.loads(request.body)
        if '3rd_party_sh_name' in received_json_data:
            third_party_sh_name = received_json_data['3rd_party_sh_name']
        else:
            missing_field_name += '3rd_party_sh_name, '
            success = False

        if 'request_mode' in received_json_data:
            request_mode = received_json_data['request_mode']
        else:
            missing_field_name += 'request_mode, '
            success = False

        if 'params' in received_json_data:
            params = received_json_data['params']
        else:
            missing_field_name += 'parameters, '
            success = False

        if '3rd_userid' in params:
            third_userid = params['3rd_userid']
        else:
            missing_field_name += '3rd_userid, '
            success = False

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field_name += 'userid, '
            success = False

        if 'account_name' in params:
            account_name = params['account_name']

        if 'token' in params:
            token = params['token']
        else:
            missing_field_name += 'token, '
            success = False

        if success == False:
            response = JsonResponse({
                "success": 'false',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "points": "null",
                "act_membership_num": "null",
                "expiration_time": "",
                "request_mode": request_mode
            })
            response.status_code = 200
            return response

        if checkIfTokenExist(token):
            balance = checkIfRecordExistAndBalance(third_party_sh_name, third_userid, account_name)
            if not balance == 'no_exist':
                error_msg = ''
                post_balance = balance
                success = 'true'
                status_code = 200
                expiration_time = datetime.datetime.now() + datetime.timedelta(30)
            else:
                error_msg = "not found the record according to these parameters"
                post_balance = 'null'
                success = 'false'
                status_code = 404
                expiration_time = 'null'
            response = JsonResponse({
                "success": success,
                "error_msg": error_msg,
                "points": post_balance,
                "act_membership_num": "null",
                "expiration_time": expiration_time,
                "request_mode": request_mode
            })
            response.status_code = status_code
            return response
        else:
            response = JsonResponse({
                "success": 'false',
                "error_msg": "token is not valid",
                "points": "null",
                "act_membership_num": "null",
                "expiration_time": "null",
                "request_mode": request_mode
            })
            response.status_code = 404
            return response

    response = JsonResponse({
        "success": 'false',
        "error_msg": "no valid parameters",
        "points": "null",
        "act_membership_num": "null",
        "expiration_time": "null",
        "request_mode": "null"
    })
    response.status_code = 404
    return response


def checkIfRecordExistAndBalance(third_party_sh_name, third_userid, account_name):
    points = [];
    if account_name == '':
        points = Point.objects.filter(third_party_sh_name__iexact=third_party_sh_name, third_userid=third_userid)
    else:
        points = Point.objects.filter(third_party_sh_name__iexact=third_party_sh_name, third_userid=third_userid,
                                      account_name=account_name)

    if len(points) >= 1:
        return points[0].balance
    else:
        return 'no_exist'