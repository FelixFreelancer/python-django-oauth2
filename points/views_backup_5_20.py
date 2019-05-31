from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# pip install mysql-connector-python
import mysql.connector
import datetime
import json

# import Point Model
from points.models import Point
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

        if checkIfTokenExist(token) == True:
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
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        sql_select_query = """ SELECT * FROM user_profile WHERE token = '""" + token + """'"""
        cursor = connection.cursor()
        result = cursor.execute(sql_select_query)
        rows = cursor.fetchall()
        connection.commit()
        print("Record select successfully into user_profile table")
        if len(rows) >= 1:
            return True
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into table {}".format(error))
        return False
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return False


def checkIfRecordExist(third_party_sh_name, third_userid, account_name):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        sql_select_query = ''
        if account_name == '':
            sql_select_query = """ SELECT * FROM points WHERE third_party_sh_name = '""" + third_party_sh_name + """' and third_userid = '""" + third_userid + """'"""
        else:
            sql_select_query = """ SELECT * FROM points WHERE third_party_sh_name = '""" + third_party_sh_name + """' and third_userid = '""" + third_userid + """' and account_name = '""" + account_name + """'"""

        cursor = connection.cursor()
        result = cursor.execute(sql_select_query)
        rows = cursor.fetchall()
        connection.commit()
        print("Record select successfully into points table")
        if len(rows) >= 1:
            # return id
            return rows[0][0]
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed selecting record into table {}".format(error))
        return False
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return False


def sumBalance(id, add_amount):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        cursor = connection.cursor()
        sql_current_balance_query = """SELECT balance FROM points WHERE id = '""" + str(id) + """"'"""
        # return balance value
        result = cursor.execute(sql_current_balance_query)
        rows = cursor.fetchall()
        current_balance = rows[0][0]

        if add_amount.isdigit() == False:
            add_amount = 0
        current_balance = int(current_balance) + int(add_amount)
        sql_sum_query = """ UPDATE points SET balance =  '""" + str(
            current_balance) + """', points_accumulate_so_far = '""" + str(
            current_balance) + """'  WHERE id = '""" + str(id) + """'"""

        result = cursor.execute(sql_sum_query)
        connection.commit()
        print("Sum balance successfully into points table")

        return current_balance
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed adding balance record into table {}".format(error))
        return 0
    print("MySQL connection is closed")
    return 0


def insertNewPoints(third_party_sh_name, third_userid, request_mode, userid, account_name, add_amount, transaction_type,
                    linked_trans_id, token):

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        if add_amount.isdigit() == False:
            add_amount = 0
        sql_insert_query = """ INSERT INTO `points`
                          (`third_party_sh_name`, `third_userid`, `request_mode`, `userid`, `account_name`, `balance`, `transaction_type`, `linked_trans_id`, `token`)
                           VALUES ('""" + third_party_sh_name + """','""" + third_userid + """','""" + request_mode + """','""" + userid + """','""" + account_name + """',""" + add_amount + """,'""" + transaction_type + """','""" + linked_trans_id + """','""" + token + """')"""
        cursor = connection.cursor()
        result = cursor.execute(sql_insert_query)
        connection.commit()
        print("New Record inserted successfully into points table")
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

        if checkIfTokenExist(token) == True:
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
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        cursor = connection.cursor()
        sql_current_balance_query = """SELECT balance FROM points WHERE id = '""" + str(id) + """"'"""
        # return balance value
        result = cursor.execute(sql_current_balance_query)
        rows = cursor.fetchall()
        current_balance = rows[0][0]

        if deduct_amount.isdigit() == False:
            deduct_amount = 0
        current_balance = int(current_balance) - int(deduct_amount)
        if current_balance < 0:
            current_balance = ''
        else:
            sql_sum_query = """ UPDATE points SET balance =  '""" + str(current_balance) + """' WHERE id = '""" + str(
                id) + """'"""
            result = cursor.execute(sql_sum_query)
        connection.commit()
        print("Deduct balance successfully into points table")

        return current_balance
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed deducting balance record into table {}".format(error))
        return 0
    print("MySQL connection is closed")
    return 0


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

        if checkIfTokenExist(token) == True:
            balance = checkIfRecordExistAndBalance(third_party_sh_name, third_userid, account_name)
            if not balance == False:
                error_msg = ''
                post_balance = balance
                success = 'true'
                status_code = 200
                expiration_time = datetime.datetime.now() + datetime.timedelta(30)
            else:
                error_msg = "not found the record according to these parameters"
                post_balance = 'null'
                deduct_time = 'null'
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
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='notification_proxy',
                                             user='root',
                                             password='')
        sql_select_query = ''
        if account_name == '':
            sql_select_query = """ SELECT balance FROM points WHERE third_party_sh_name = '""" + third_party_sh_name + """' and third_userid = '""" + third_userid + """'"""
        else:
            sql_select_query = """ SELECT balance FROM points WHERE third_party_sh_name = '""" + third_party_sh_name + """' and third_userid = '""" + third_userid + """' and account_name = '""" + account_name + """'"""

        cursor = connection.cursor()
        result = cursor.execute(sql_select_query)
        rows = cursor.fetchall()
        connection.commit()
        print("Record select balance successfully into points table")
        if len(rows) >= 1:
            # return id
            return rows[0][0]
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
