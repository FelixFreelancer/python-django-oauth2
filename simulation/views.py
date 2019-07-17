from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import datetime
import json

import base64
from Crypto.Cipher import AES

# import scrap functions 
from simulation.third_party_scrap.scrap import scrapCsair, scrapAsiamiles, scrapHilton, scrapIhg, scrapMoneyBack

# import model
from simulation.models import Simulation, Cnonce
from points.models import Point
# import constants form settings.py
from django.conf import settings


# Create your views here.
@csrf_exempt
def getToken_v_01(request):
    if request.method == 'GET':
        param = request.GET
        response = getToken(param)
    else:
        response = JsonResponse({"msg": "Empty API!"})
        response.status_code = 500
    return response

@csrf_exempt
def getToken_v_11(request):
    if request.method == 'GET' and 'params' in request.GET:
        encrypted_str = request.GET['params'].replace(" ", "+")
        decrypted_str = decrypt(encrypted_str)
        decrypted_param = json.loads(decrypted_str)
        response = getToken(decrypted_param)
    else:
        response = JsonResponse({"msg": "Empty API!"})
        response.status_code = 500
    return response

@csrf_exempt
def getToken_v_12(request):
    if request.method == 'GET' and 'param' in request.GET:
        encrypted_str = request.GET['param'].replace(" ", "+")
        decrypted_str = decrypt(encrypted_str)
        decrypted_param = json.loads(decrypted_str)
        response = getTokenV12(decrypted_param)
    else:
        response = JsonResponse({"msg": "Empty API!"})
        response.status_code = 500
    return response


def getToken(params):
    response = JsonResponse({"msg": "Empty API!"})
    response.status_code = 500
    if 'request_mode' in params:
        requestMode = params['request_mode']
    else:
        requestMode = 'simulation'
    if requestMode == 'simulation':
        token = generateToken()
        expiration_date = datetime.datetime.now() + datetime.timedelta(30)
        expiration_format_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        success = "true"
        error_msg = ""
        request_mode = requestMode
        userid = ''
        refresh_request = ''
        missing_field = False
        missing_field_name = ''
        third_party_sh_name = ''
        third_password = ''
        third_userid = ''
        third_registered_phone_number = ''
        scrap_success = True
        resoponse_status_code = 200
        original_data = ''

        if 'refresh_request' in params:
            refresh_request = params['refresh_request']

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field = True
            missing_field_name += 'userid, '

        if not '3rd_party_sh_name' in params:
            missing_field = True
            missing_field_name += '3rd_party_sh_name, '
        else:
            third_party_sh_name = params['3rd_party_sh_name']

        if not '3rd_password' in params:
            missing_field = True
            missing_field_name += '3rd_password, '
        else:
            third_password = params['3rd_password']

        if not '3rd_userid' in params:
            missing_field = True
            missing_field_name += '3rd_userid, '
        else:
            third_userid = params['3rd_userid']

        if not '3rd_registered_phone_number' in params:
            missing_field = True
            missing_field_name += '3rd_registered_phone_number, '
        else:
            third_registered_phone_number = params['3rd_registered_phone_number']

        if missing_field == True:
            response = JsonResponse({
                "success": 'false',
                "token": 'null',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "expiration_time": 'null',
                "request_mode": requestMode
            })
            response.status_code = resoponse_status_code
            return response

        store_data = {"third_party_sh_name": third_party_sh_name, "request_mode": request_mode,
                      "third_userid": third_userid, "userid": userid, "account_name": "", "balance": 0,
                      "transaction_type": ""
            , "linked_trans_id": "", "expiration_time": expiration_format_date, "points_accumulate_so_far": 0,
                      "member_ship_no": "", "token": token, "reward_point": "", "member_id": ""
            , "expiration_date": "", "remaining_balance": "", "points_to_be_expire_by_monthend": "",
                      "stays_balance": "", "nights_balance": ""
            , "points_balance": "", "point_accumulated": "", "nights_accumulated": "", "member_name": ""}

        # csair's case: remaining_balance, points_to_be_expire_by_monthend field will be used
        if third_party_sh_name.lower() == 'csair_tmp':
            result_data = json.loads(scrapCsair(third_userid, third_password))
            store_data['remaining_balance'] = result_data["remaining_balance"]
            store_data['points_to_be_expire_by_monthend'] = result_data["points_to_be_expire_by_monthend"]

        if third_party_sh_name.lower() == 'asiamiles_tmp':
            needUpdate = checkIfMustUpdate('{"third_party_sh_name": "asiamiles", "third_userid": "' + third_userid + '"}')
            if needUpdate:
                result_data = json.loads(scrapAsiamiles(third_userid, third_password))
                store_data['reward_point'] = str(result_data["rewardPoint"])
                store_data['member_id'] = str(result_data["memberId"])
                store_data['expiration_date'] = str(result_data["expirationDate"])
                scrap_success = result_data['error']
            else:
                # original_data = needUpdate
                scrap_success = False

        if third_party_sh_name.lower() == 'hilton_tmp':
            result_data = json.loads(scrapHilton(third_userid, third_password))
            store_data['stays_balance'] = result_data["stays_balance"]
            store_data['nights_balance'] = result_data["nights_balance"]
            store_data['points_balance'] = result_data["points_balance"]

        if third_party_sh_name.lower() == 'ihg_tmp':
            result_data = json.loads(scrapIhg(third_userid, third_password))
            store_data['points_balance'] = result_data["points_balance"]
            store_data['point_accumulated'] = result_data["point_accumulated"]
            store_data['nights_accumulated'] = result_data["nights_accumulated"]

        if third_party_sh_name.lower() == 'moneyback_tmp':
            needUpdate = checkIfMustUpdate('{"third_party_sh_name": "moneyback", "third_userid": "' + third_userid + '"}')
            if needUpdate:
                result_data = json.loads(scrapMoneyBack(third_userid, third_password))
                store_data['member_id'] = result_data["memberid"]
                store_data['member_name'] = result_data["membername"]
                store_data['points_balance'] = result_data["points_balance"]
                scrap_success = result_data['error']
            else:
                scrap_success = False

        if str(refresh_request).lower() == 'yes':
            updateToken(token, expiration_format_date, success, error_msg, request_mode, userid,
                        third_party_sh_name, third_password, third_userid, third_registered_phone_number)
        else:
            # if scrap_success == True:
            saveScrapResultstoPoints(store_data)
            saveToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
                      third_password, third_userid, third_registered_phone_number)
            # else:
            #     success = 'false'
            #     token = 'null'
            #     error_msg = "can't get scraping result"
            #     resoponse_status_code = 500
            #     expiration_format_date = 'null'

        return_json_data = {
            "success": success,
            "token": token,
            "error_msg": error_msg,
            "expiration_time": expiration_format_date,
            "request_mode": requestMode
        }
        response = JsonResponse({
            "result": encrypt(str(return_json_data)).decode('utf-8'),
        })
        response.status_code = resoponse_status_code
    return response


def getTokenV12(params):
    response = JsonResponse({"msg": "Empty API!"})
    response.status_code = 500
    if 'request_mode' in params:
        requestMode = params['request_mode']
    else:
        requestMode = 'simulation'
    if requestMode == 'simulation':
        token = generateToken()
        expiration_date = datetime.datetime.now() + datetime.timedelta(30)
        expiration_format_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        success = "true"
        error_msg = ""
        request_mode = requestMode
        userid = ''
        refresh_request = ''
        missing_field = False
        missing_field_name = ''
        third_party_sh_name = ''
        third_password = ''
        third_userid = ''
        third_registered_phone_number = ''
        scrap_success = True
        resoponse_status_code = 200
        original_data = ''
        nonce = ''
        api_timestamp = ''

        if 'refresh_request' in params:
            refresh_request = params['refresh_request']

        if 'userid' in params:
            userid = params['userid']
        else:
            missing_field = True
            missing_field_name += 'userid, '

        if not '3rd_party_sh_name' in params:
            missing_field = True
            missing_field_name += '3rd_party_sh_name, '
        else:
            third_party_sh_name = params['3rd_party_sh_name']

        if not '3rd_password' in params:
            missing_field = True
            missing_field_name += '3rd_password, '
        else:
            third_password = params['3rd_password']

        if not '3rd_userid' in params:
            missing_field = True
            missing_field_name += '3rd_userid, '
        else:
            third_userid = params['3rd_userid']

        if not '3rd_registered_phone_number' in params:
            missing_field = True
            missing_field_name += '3rd_registered_phone_number, '
        else:
            third_registered_phone_number = params['3rd_registered_phone_number']

        if 'cnounce' in params:
            nonce = params['cnounce']
        else:
            missing_field_name += 'cnounce, '
            missing_field = True

        if 'api_timestamp' in params:
            api_timestamp = params['api_timestamp']
        else:
            missing_field_name += 'api_timestamp, '
            missing_field = True

        if missing_field == True:
            response = JsonResponse({
                "success": 'false',
                "token": 'null',
                "error_msg": missing_field_name[0: len(missing_field_name) - 2] + " are missing.",
                "expiration_time": 'null',
                "request_mode": requestMode
            })
            response.status_code = resoponse_status_code
            return response
        nonce_check_result = checkNonceAndTimeStamp(nonce, api_timestamp)
        if not nonce_check_result == 'success':
            response = JsonResponse({
                "success": 'false',
                "token": 'null',
                "error_msg": nonce_check_result,
                "expiration_time": 'null',
                "request_mode": requestMode
            })
            response.status_code = 200
            return response

        store_data = {"third_party_sh_name": third_party_sh_name, "request_mode": request_mode,
                      "third_userid": third_userid, "userid": userid, "account_name": "", "balance": 0,
                      "transaction_type": "", "linked_trans_id": "", "expiration_time": expiration_format_date,
                      "points_accumulate_so_far": 0, "member_ship_no": "", "token": token, "reward_point": "",
                      "member_id": "", "expiration_date": "", "remaining_balance": "",
                      "points_to_be_expire_by_monthend": "", "stays_balance": "", "nights_balance": "",
                      "points_balance": "", "point_accumulated": "", "nights_accumulated": "", "member_name": ""}

        # csair's case: remaining_balance, points_to_be_expire_by_monthend field will be used
        if third_party_sh_name.lower() == 'csair_tmp':
            result_data = json.loads(scrapCsair(third_userid, third_password))
            store_data['remaining_balance'] = result_data["remaining_balance"]
            store_data['points_to_be_expire_by_monthend'] = result_data["points_to_be_expire_by_monthend"]

        if third_party_sh_name.lower() == 'asiamiles_tmp':
            needUpdate = checkIfMustUpdate('{"third_party_sh_name": "asiamiles", "third_userid": "' + third_userid + '"}')
            if needUpdate:
                result_data = json.loads(scrapAsiamiles(third_userid, third_password))
                store_data['reward_point'] = str(result_data["rewardPoint"])
                store_data['member_id'] = str(result_data["memberId"])
                store_data['expiration_date'] = str(result_data["expirationDate"])
                scrap_success = result_data['error']
            else:
                # original_data = needUpdate
                scrap_success = False

        if third_party_sh_name.lower() == 'hilton_tmp':
            result_data = json.loads(scrapHilton(third_userid, third_password))
            store_data['stays_balance'] = result_data["stays_balance"]
            store_data['nights_balance'] = result_data["nights_balance"]
            store_data['points_balance'] = result_data["points_balance"]

        if third_party_sh_name.lower() == 'ihg_tmp':
            result_data = json.loads(scrapIhg(third_userid, third_password))
            store_data['points_balance'] = result_data["points_balance"]
            store_data['point_accumulated'] = result_data["point_accumulated"]
            store_data['nights_accumulated'] = result_data["nights_accumulated"]

        if third_party_sh_name.lower() == 'moneyback_tmp':
            needUpdate = checkIfMustUpdate('{"third_party_sh_name": "moneyback", "third_userid": "' + third_userid + '"}')
            if needUpdate:
                result_data = json.loads(scrapMoneyBack(third_userid, third_password))
                store_data['member_id'] = result_data["memberid"]
                store_data['member_name'] = result_data["membername"]
                store_data['points_balance'] = result_data["points_balance"]
                scrap_success = result_data['error']

            else:
                scrap_success = False

        if str(refresh_request).lower() == 'yes':
            updateToken(token, expiration_format_date, success, error_msg, request_mode, userid,
                        third_party_sh_name, third_password, third_userid, third_registered_phone_number)
        else:
            # if scrap_success == True:
            saveScrapResultstoPoints(store_data)
            saveToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
                      third_password, third_userid, third_registered_phone_number)
            # else:
            #     success = 'false'
            #     token = 'null'
            #     error_msg = "can't get scraping result"
            #     resoponse_status_code = 500
            #     expiration_format_date = 'null'

        return_json_data = {
            "success": success,
            "token": token,
            "error_msg": error_msg,
            "expiration_time": expiration_format_date,
            "request_mode": requestMode
        }
        response = JsonResponse({
            "result": encrypt(str(return_json_data)).decode('utf-8'),
        })
        response.status_code = resoponse_status_code
    return response


def generateToken():
    token = get_random_string(length=64)
    return token


def saveToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
              third_password, third_userid, third_registered_phone_number):
    save_user = Simulation(token=token, expiration_time=expiration_format_date, success=success, error_msg=error_msg,
                           request_mode=request_mode, userid=userid, third_party_sh_name=third_party_sh_name,
                           third_password=third_password, third_userid=third_userid,
                           third_registered_phone_number=third_registered_phone_number)
    save_user.save()


def updateToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
                third_password, third_userid, third_registered_phone_number):
    update_user = Simulation.objects.filter(userid=userid).update(token=token, expiration_time=expiration_format_date,
                                                                  success=success, error_msg=error_msg,
                                                                  request_mode=request_mode,
                                                                  third_party_sh_name=third_party_sh_name,
                                                                  third_password=third_password,
                                                                  third_userid=third_userid,
                                                                  third_registered_phone_number=third_registered_phone_number)


def saveScrapResultstoPoints(store_data):
    points = Point(third_party_sh_name=str(store_data['third_party_sh_name']),
                   request_mode=str(store_data['request_mode']), third_userid=str(store_data['third_userid']),
                   userid=str(store_data['userid']), account_name=str(store_data['account_name']),
                   balance=str(store_data['balance']),
                   transaction_type=str(store_data['transaction_type']),
                   linked_trans_id=str(store_data['linked_trans_id']),
                   expiration_time=str(store_data['expiration_time']),
                   points_accumulate_so_far=str(store_data['points_accumulate_so_far']),
                   member_ship_no=str(store_data['member_ship_no']), token=str(store_data['token']),
                   reward_point=str(store_data['reward_point']), member_id=str(store_data['member_id']),
                   expiration_date=str(store_data['expiration_date']),
                   remaining_balance=str(store_data['remaining_balance']),
                   points_to_be_expire_by_monthend=str(store_data['points_to_be_expire_by_monthend']),
                   stays_balance=str(store_data['stays_balance']),
                   nights_balance=str(store_data['nights_balance']), points_balance=str(store_data['points_balance']),
                   point_accumulated=str(store_data['point_accumulated']),
                   nights_accumulated=str(store_data['nights_accumulated']), member_name=str(store_data['member_name']),
                   updated_at=datetime.datetime.now())
    points.save()


def checkIfMustUpdate(params):
    expiration_format_date = (datetime.datetime.now() - datetime.timedelta(0, 240)).strftime("%Y-%m-%d %H:%M:%S")
    print(params)
    params = json.loads(str(params))
    check_points = Point.objects.filter(**params).filter(updated_at__gte=expiration_format_date).order_by('updated_at')[
                   :1]
    if len(check_points) == 0:
        return True
    else:
        return False


def checkNonceAndTimeStamp(nonce, timestamp):
    # timestamp checking
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=settings.EXPIRATION_SEC)
    current_datetime = datetime.datetime.now()
    if current_datetime > timestamp_datetime:
        return 'request parameters expired'
    # nonce checking
    record_count = Cnonce.objects.filter(nonce=nonce).count()
    if record_count >= 1:
        return 'Token nonce isn\'t valid'
    new_nonce = Cnonce(nonce=nonce, timestamp=timestamp)
    new_nonce.save()
    return 'success'


def pad(text):
    text_length = len(text)
    amount_to_pad = AES.block_size - (text_length % AES.block_size)
    if amount_to_pad == 0:
        amount_to_pad = AES.block_size
    pads = chr(amount_to_pad).encode('utf8')
    return text + pads * amount_to_pad


def encrypt(raw):
    key = settings.ENCRYPTION_KEY
    iv = settings.ENCRYPTION_IV
    key = key[0:16]
    raw = raw.encode("utf8")
    raws = pad(raw)
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return base64.b64encode(cipher.encrypt(raws))


def __unpad(text):
    pad = ord(text[-1])
    return text[:-pad]


def decrypt(enc):
    key = settings.ENCRYPTION_KEY
    iv = settings.ENCRYPTION_IV
    enc = base64.b64decode(enc)
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return __unpad(cipher.decrypt(enc).decode("utf-8"))
