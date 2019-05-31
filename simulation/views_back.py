from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# pip install mysql-connector-python
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from django.utils.crypto import get_random_string
import requests
import urllib.parse
import datetime
import json

import base64
from Crypto.Cipher import AES

# import scrap functions
from simulation.third_party_scrap.scrap import scrapCsair, scrapAsiamiles, scrapHilton, scrapIhg, scrapMoneyBack

# Create your views here.
USRENAME = 'root'
PASSWORD = ''
DATABASE = 'notification_proxy'

ENCRYPTION_KEY = 'B37AD9F661A50496'
ENCRYPTION_IV = 'A496F48259F76DEE'


def getTokenFromOrgUrl(request):
    if request.method == 'GET':
        param = request.GET
        response = getToken(param)
    else:
        response = JsonResponse({"msg": "Empty API!"})
        response.status_code = 500
    return response


def getTokenFromEncryptUrl(request):
    if request.method == 'GET' and 'params' in request.GET:
        encrypted_str = request.GET['params'].replace(" ", "+")
        decrypted_str = decrypt(encrypted_str)
        decrypted_param = json.loads(decrypted_str)
        response = getToken(decrypted_param)
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
        if third_party_sh_name.lower() == 'csair':
            result_data = json.loads(scrapCsair(third_userid, third_password))
            store_data['remaining_balance'] = result_data["remaining_balance"]
            store_data['points_to_be_expire_by_monthend'] = result_data["points_to_be_expire_by_monthend"]

        if third_party_sh_name.lower() == 'asiamiles':
            needUpdate = checkIfMustUpdate({'third_party_sh_name': 'asiamiles', 'third_userid': third_userid})
            if not needUpdate == False:
                result_data = json.loads(scrapAsiamiles(third_userid, third_password))
                store_data['reward_point'] = str(result_data["rewardPoint"])
                store_data['member_id'] = str(result_data["memberId"])
                store_data['expiration_date'] = str(result_data["expirationDate"])
                scrap_success = result_data['error']
            else:
                # original_data = needUpdate
                scrap_success = False

        if third_party_sh_name.lower() == 'hilton':
            result_data = json.loads(scrapHilton(third_userid, third_password))
            store_data['stays_balance'] = result_data["stays_balance"]
            store_data['nights_balance'] = result_data["nights_balance"]
            store_data['points_balance'] = result_data["points_balance"]

        if third_party_sh_name.lower() == 'ihg':
            result_data = json.loads(scrapIhg(third_userid, third_password))
            store_data['points_balance'] = result_data["points_balance"]
            store_data['point_accumulated'] = result_data["point_accumulated"]
            store_data['nights_accumulated'] = result_data["nights_accumulated"]

        if third_party_sh_name.lower() == 'moneyback':
            needUpdate = checkIfMustUpdate({'third_party_sh_name': 'moneyback', 'third_userid': third_userid})
            if not needUpdate == False:
                result_data = json.loads(scrapMoneyBack(third_userid, third_password))
                store_data['member_id'] = result_data["memberid"]
                store_data['member_name'] = result_data["membername"]
                store_data['points_balance'] = result_data["points_balance"]
                scrap_success = result_data['error']
            else:
                # original_data = needUpdate
                scrap_success = False

        if str(refresh_request).lower() == 'yes':
            if userid == '':
                success = 'false'
                error_msg = 'userid parameters is missing'
                token = 'null'
                expiration_format_date = 'null'
                store_data['expiration_time'] = expiration_format_date
                store_data['token'] = token
            else:
                updateToken(token, expiration_format_date, success, error_msg, request_mode, userid,
                            third_party_sh_name, third_password, third_userid, third_registered_phone_number)
        else:
            if scrap_success == True:
                saveScrapResultstoPoints(store_data)
                saveToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
                          third_password, third_userid, third_registered_phone_number)
            else:
                success = 'false'
                token = 'null'
                error_msg = "can't get scraping result"
                resoponse_status_code = 500
                expiration_format_date = 'null'

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
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database=DATABASE,
                                             user=USRENAME,
                                             password=PASSWORD)
        sql_insert_query = """ INSERT INTO `user_profile`
                          (`token`, `expiration_time`, `success`, `error_msg`, `request_mode`, `userid`, `third_party_sh_name`, `third_password`, `third_userid`, `third_registered_phone_number`)
                           VALUES ('""" + token + """','""" + expiration_format_date + """','""" + success + """','""" + error_msg + """','""" + request_mode + """','""" + userid + """','""" + third_party_sh_name + """','""" + third_password + """','""" + third_userid + """','""" + third_registered_phone_number + """')"""
        cursor = connection.cursor()
        result = cursor.execute(sql_insert_query)
        connection.commit()
        print("Record inserted successfully into token table")
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return


def updateToken(token, expiration_format_date, success, error_msg, request_mode, userid, third_party_sh_name,
                third_password, third_userid, third_registered_phone_number):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database=DATABASE,
                                             user=USRENAME,
                                             password=PASSWORD)
        sql_update_query = """ UPDATE `user_profile` SET token ='""" + token + """', expiration_time ='""" + expiration_format_date + """', success='""" + success + """', error_msg='""" + error_msg + """', request_mode ='""" + request_mode + """', third_party_sh_name='""" + third_party_sh_name + """', third_password='""" + third_password + """', third_userid='""" + third_userid + """', third_registered_phone_number='""" + third_registered_phone_number + """' WHERE userid='""" + userid + """'"""
        cursor = connection.cursor()
        result = cursor.execute(sql_update_query)
        connection.commit()
        print("Record updated successfully into token table")
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return


def saveScrapResultstoPoints(store_data):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        sql_insert_query = """ INSERT INTO `points`
                          (`third_party_sh_name`,  `request_mode`, `third_userid`, `userid`, `account_name`, `balance`, `transaction_type`, `linked_trans_id`, `expiration_time`
                            , `points_accumulate_so_far`,  `member_ship_no`,  `token`,  `reward_point`,  `member_id`,  `expiration_date`,  `remaining_balance`,  `points_to_be_expire_by_monthend`
                            , `stays_balance`, `nights_balance`, `points_balance`, `point_accumulated`, `nights_accumulated`, `member_name`, `updated_at`)
                           VALUES ('""" + str(store_data['third_party_sh_name']) + """','""" + str(
            store_data['request_mode']) + """','""" + str(store_data['third_userid']) + """','""" + str(
            store_data['userid']) \
                           + """','""" + str(store_data['account_name']) + """','""" + str(
            store_data['balance']) + """','""" + str(store_data['transaction_type']) + """','""" + str(
            store_data['linked_trans_id']) \
                           + """','""" + str(store_data['expiration_time']) + """','""" + str(
            store_data['points_accumulate_so_far']) + """','""" + str(store_data['member_ship_no']) + """','""" + str(
            store_data['token']) \
                           + """','""" + str(store_data['reward_point']) + """','""" + str(
            store_data['member_id']) + """','""" + str(store_data['expiration_date']) + """','""" + str(
            store_data['remaining_balance']) \
                           + """','""" + str(store_data['points_to_be_expire_by_monthend']) + """','""" + str(
            store_data['stays_balance']) + """','""" + str(store_data['nights_balance']) + """','""" + str(
            store_data['points_balance']) \
                           + """','""" + str(store_data['point_accumulated']) + """','""" + str(
            store_data['nights_accumulated']) + """','""" + str(store_data['member_name']) + """', NOW())"""
        cursor = connection.cursor()
        result = cursor.execute(sql_insert_query)
        connection.commit()
        print("Scrapping results inserted successfully into points table")
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into table {}".format(error))
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return


def checkIfMustUpdate(params):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        sql_select_query = """ SELECT * FROM points WHERE """

        for l_value, r_value in params.items():
            sql_select_query = sql_select_query + l_value + "='" + r_value + "' and "

        cursor = connection.cursor()
        expiration_date = datetime.datetime.now() - datetime.timedelta(0, 240)
        expiration_format_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        sql_select_query = sql_select_query + " updated_at >= '" + expiration_format_date + "' order by updated_at desc limit 1"
        result = cursor.execute(sql_select_query)
        rows = cursor.fetchall()
        connection.commit()
        print("Check if the record exists or not on the points table")
        if len(rows) == 0:
            # return updated at
            # updated_at = rows[0][0]
            return True
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed selecting balance record into table {}".format(error))
        return False
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return False


def pad(text):
    text_length = len(text)
    amount_to_pad = AES.block_size - (text_length % AES.block_size)
    if amount_to_pad == 0:
        amount_to_pad = AES.block_size
    pads = chr(amount_to_pad).encode('utf8')
    return text + pads * amount_to_pad


def encrypt(raw):
    key = ENCRYPTION_KEY
    iv = ENCRYPTION_IV
    key = key[0:16]
    raw = raw.encode("utf8")
    raws = pad(raw)
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return base64.b64encode(cipher.encrypt(raws))


def __unpad(text):
    pad = ord(text[-1])
    return text[:-pad]


def decrypt(enc):
    key = ENCRYPTION_KEY
    iv = ENCRYPTION_IV
    enc = base64.b64decode(enc)
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    return __unpad(cipher.decrypt(enc).decode("utf-8"))