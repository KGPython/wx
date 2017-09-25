# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/8/24 14:24'
import datetime,json,requests,time

from django.core.cache import caches

from api.models import LogWx
from utils import wx,consts,method,data

def gift_compare_order(offset=0):
    res = {}
    res['status'] = 0
    res_get = get_Wx_order(offset)
    if res_get['status'] == 0:
        offset = res_get['offset']
        total_count = res_get['total_count']
        wx_orders = res_get['wx_orders']
        data.local_save_gift_order(wx_orders)
        if total_count > (offset + 1) * 100:
            gift_compare_order(offset + 1)

    else:
        res['status'] = 1

    return res


def get_Wx_order(begin_time,end_time,offset=0):
    offset_now = offset * 100
    access_token = caches['default'].get('wx_kgcs_access_token', '')
    if not access_token:
        wx.get_access_token('kgcs', consts.KG_APPID, consts.KG_APPSECRET)

    rep_data = order_batchget(access_token,begin_time,end_time,offset_now)
    res = {}
    if rep_data['errmsg'] == 'ok':
        total_count = rep_data['total_count']
        wx_orders = rep_data['order_list']
        res['status'] = 0
        res['offset'] = offset
        res['total_count'] = total_count
        res['wx_orders'] = wx_orders
    else:
        res['status'] = 1
        LogWx.objects.create(type='6', errmsg=rep_data['errmsg'], errcode=rep_data['errcode'],
                             remark='cron_giftcard_wx_local')
    return res


def order_batchget(access_token,begin,end,offset=0,count=100):
    url = "https://api.weixin.qq.com/card/giftcard/order/batchget?access_token={access_token}" \
        .format(access_token=access_token)
    data = {
        "begin_time": begin,
        "end_time": end,
        "sort_type": "DESC",
        "offset": offset,
        "count": count
    }
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    rep = requests.post(url, data=data)
    rep_data = json.loads(rep.text)

    return rep_data


def change_balance(order,access_token):
    """
    修改礼品卡余额
    :param order:
    :param access_token:
    :return:
    """
    code = order['CardNo'].strip()
    card_id = order['wx_card_id']
    balance = float(order['detail'])
    serial = order['PurchSerial']
    remark = 'PurchSerial:{serial},CardNo:{code},detail:{balance},card_id:{card_id}' \
        .format(serial=serial, code=code, balance=str(float(balance)), card_id=card_id)
    try:
        rep_data = doChangeBalance(access_token,code,card_id,balance)
        if 'repeat_status' in order :
            if rep_data['errcode'] == 0:
                LogWx.objects.filter(id=order['id']).update(repeat_status='1')
            else:
                LogWx.objects.filter(id=order['id']).update(add_time=datetime.datetime.now())
        else:
            log = LogWx()
            log.type = 2
            log.errmsg = rep_data['errmsg']
            log.errcode = rep_data['errcode']
            log.remark = remark
            if rep_data['errcode'] != 0:
                log.repeat_status = '0'
            log.save()
    except Exception as e:
        print(e)
        method.CreateLog('2', '1202', e, 'method:change_balance error')


def doChangeBalance(access_token,code,card_id,balance):
    url = 'https://api.weixin.qq.com/card/generalcard/updateuser?access_token={token}' \
        .format(token=access_token)
    data = {
        "code": code,
        "card_id": card_id,
        "balance": balance * 100
    }

    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    rep = requests.post(url, data=data)
    rep_data = json.loads(rep.text)
    return rep_data

def getCardCodeInfo(access_token,card_id,code):
    """
    查询code信息
    :param access_token:
    :param card_id:
    :param code:
    :return:
    """
    url = 'https://api.weixin.qq.com/card/code/get?access_token={token}' \
        .format(token=access_token)
    data = {
        "card_id": card_id,
        "code": code,
        "check_consume": True
    }
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    rep = requests.post(url, data=data)
    rep_data = json.loads(rep.text)

    return rep_data


def getOrder(access_token,order_id):
    """
    单个礼品卡订单查询
    :param access_token:
    :param order_id:
    :return:
    """
    url = 'https://api.weixin.qq.com/card/giftcard/order/get?access_token={token}' \
        .format(token=access_token)
    data = {"order_id": order_id}
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    client = requests.Session()
    rep = client.post(url, data=data, headers={'Connection': 'close'})
    rep_data = json.loads(rep.text)

    return  rep_data

def deleteCard(access_token,card_id):
    url = 'https://api.weixin.qq.com/card/delete?access_token={token}' \
        .format(token=access_token)
    data_post = {"card_id": card_id}
    data_post = json.dumps(data_post, ensure_ascii=False).encode('utf-8')

    rep = requests.post(url, data=data_post)
    rep_data = json.loads(rep.text)

    return rep_data


def oderRefund(access_token,order_id):
    url = 'https://api.weixin.qq.com/card/giftcard/order/refund?access_token={token}' \
        .format(token=access_token)
    data = {
        "order_id": order_id
    }
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    rep = requests.post(url, data=data)
    rep_data = json.loads(rep.text)

    return rep_data