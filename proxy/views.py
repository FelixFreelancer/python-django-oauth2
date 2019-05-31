from __future__ import print_function

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
# import constants form settings.py
from django.conf import settings

import base64
from Crypto.Cipher import AES

# import models
from proxy.models import UseNotify, BuyNotify


# Create your views here.
@csrf_exempt
def buyNotify(request):
    return_data = "success"
    if request.method == 'POST':
        try:
            projectName = request.POST['projectName']
            shopName = request.POST['shopName']
            goodsName = request.POST['goodsName']
            couponCode = request.POST['couponCode']
            buyAmount = request.POST['buyAmount']
            buyTime = request.POST['buyTime']
            belongArea = request.POST['belongArea']
        except Exception as e:
            response = JsonResponse({"error": str(e) + " is not defined"})
            response.status_code = 404
            return response
    param_project_name = projectName.strip()
    param_shop_name = shopName.strip()
    param_goods_name = goodsName.strip()
    param_coupon_code = couponCode.strip()
    param_buy_amount = buyAmount.strip()
    param_buy_time = buyTime.strip()
    param_belong_area = belongArea.strip()
    if param_project_name == '':
        throwParamException('projectName')
    if param_shop_name == '':
        throwParamException('shopName')
    if param_goods_name == '':
        throwParamException('goodsName')
    if param_coupon_code == '':
        throwParamException('couponCode')
    if param_buy_amount == '':
        throwParamException('buyAmount')
    if param_buy_time == '':
        throwParamException('buyTime')
    if param_belong_area == '':
        throwParamException('belongArea')
    save_db_buy(param_project_name, param_shop_name, param_goods_name, param_coupon_code, param_buy_amount,
                param_buy_time, param_belong_area)
    data_param = '{"params":{' + '"projectName":"' + param_project_name + '","shopName":"' + param_shop_name + '","goodsName":"' + param_goods_name + '","couponCode":"' + param_coupon_code + '","buyAmount":"' + param_buy_amount + '","buyTime":"' + param_buy_time + '","belongArea":"' + param_belong_area + '"},"type":"buyNotify"}'
    return_val = requestApi(data_param)
    save_db_result('buynotify', return_val)
    return HttpResponse(return_val)


@csrf_exempt
def useNotify(request):
    return_data = "success"
    if request.method == 'POST':
        try:
            projectName = request.POST['projectName']
            shopName = request.POST['shopName']
            goodsName = request.POST['goodsName']
            couponCode = request.POST['couponCode']
            buyAmount = request.POST['buyAmount']
            buyTime = request.POST['buyTime']
            useStore = request.POST['useStore']
            useTime = request.POST['useTime']
            useAmount = request.POST['useAmount']
            belongArea = request.POST['belongArea']
        except Exception as e:
            response = JsonResponse({"error": str(e) + " is not defined"})
            response.status_code = 404
            return response
    param_project_name = projectName.strip()
    param_shop_name = shopName.strip()
    param_goods_name = goodsName.strip()
    param_coupon_code = couponCode.strip()
    param_buy_amount = buyAmount.strip()
    param_buy_time = buyTime.strip()
    param_use_store = useStore.strip()
    param_use_time = useTime.strip()
    param_use_amount = useAmount.strip()
    param_belong_area = belongArea.strip()
    if param_project_name == '':
        throwParamException('projectName')
    if param_shop_name == '':
        throwParamException('shopName')
    if param_goods_name == '':
        throwParamException('goodsName')
    if param_coupon_code == '':
        throwParamException('couponCode')
    if param_buy_amount == '':
        throwParamException('buyAmount')
    if param_buy_time == '':
        throwParamException('buyTime')
    if param_use_store == '':
        throwParamException('useStore')
    if param_use_time == '':
        throwParamException('useTime')
    if param_use_amount == '':
        throwParamException('useAmount')
    if param_belong_area == '':
        throwParamException('belongArea')
    save_db_use(param_project_name, param_shop_name, param_goods_name, param_coupon_code, param_buy_amount,
                param_buy_time, param_use_store, param_use_time, param_use_amount, param_belong_area)
    data_param = {"type": "useNotify",
                  "params": {
                      "projectName": param_project_name,
                      "shopName": param_shop_name,
                      "goodsName": param_goods_name,
                      "couponCode": param_coupon_code,
                      "buyAmount": param_buy_amount,
                      "buyTime": param_buy_time,
                      "useStore": param_use_store,
                      "useTime": param_use_time,
                      "useAmount": param_use_amount,
                      "belongArea": param_belong_area
                  }
                  }
    return_val = requestApi(str(data_param))
    save_db_result('usenotify', return_val)
    return HttpResponse(return_val)


def throwParamException(param):
    response = JsonResponse({"error": str(param) + " is empty, this field is required!"})
    response.status_code = 403
    return response


def save_db_buy(param_project_name, param_shop_name, param_goods_name, param_coupon_code, param_buy_amount,
                param_buy_time, param_belong_area):
    buynotify = BuyNotify(projectName=param_project_name, shopName=param_shop_name, goodsName=param_goods_name,
                          couponCode=param_coupon_code,
                          buyAmount=param_buy_amount, buyTime=param_buy_time, belongArea=param_belong_area)
    buynotify.save()


def save_db_use(param_project_name, param_shop_name, param_goods_name, param_coupon_code, param_buy_amount,
                param_buy_time, param_use_store, param_use_time, param_use_amount, param_belong_area):
    usenotify = UseNotify(projectName=param_project_name, shopName=param_shop_name, goodsName=param_goods_name,
                          couponCode=param_coupon_code,
                          buyAmount=param_buy_amount, buyTime=param_buy_time, useStore=param_use_store,
                          useTime=param_use_time, useAmount=param_use_amount, belongArea=param_belong_area)
    usenotify.save()


def save_db_result(tableName, result):
    if tableName == 'buynotify':
        BuyNotify.objects.latest('id').update(result=result)
    else:
        UseNotify.objects.latest('id').update(result=result)


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


def requestApi(data_param):
    try:
        enc_str = encrypt(data_param)
        response = requests.post('https://cloudback.bcpon.com/bcponBack/callback/boc', data=enc_str)
        print(response.text)
        return str(response.content)
        # return response.content
    except requests.exceptions.RequestException as e:
        print("error!")
        print(e)
