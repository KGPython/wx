# -*-  coding:utf-8 -*-
# __author__ = ''
# __date__ = '2017/4/19 14:04'
import datetime, time,requests,json
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from django.core.cache import caches
from django.http import HttpResponse

from admin.models import GiftCardCode, GiftBalanceChangeLog,ShopOrder
from api.models import LogWx
from utils import consts, method,wx,giftcard,data


def cron_get_ikg_token():
    '''
    获取并缓存 爱宽广access_token
    :return: access_token
    '''
    app_id = consts.APPID
    secret = consts.APPSECRET
    token = wx.get_access_token('ikg', app_id, secret, )
    return HttpResponse(token)


def cron_get_kgcs_token():
    """
    获取并缓存 宽广超市access_token
    :return: access_token
    """
    app_id = consts.KG_APPID
    secret = consts.KG_APPSECRET
    token = wx.get_access_token('kgcs', app_id, secret)
    return HttpResponse(token)


def cron_send_temp():
    app_id = consts.APPID
    secret = consts.APPSECRET
    access_token = caches['default'].get('wx_ikg_access_token', '')
    if not access_token:
        access_token = wx.get_access_token('ikg', app_id, secret)

    orders = data.get_user_order()
    if len(orders)>0:
        wechat_users = data.get_wechat_users(orders)
        try:
            threads = []
            msg_list = []
            for wechat_user in wechat_users:
                userId = wechat_user['membernumber']
                for order in orders:
                    if order['CardNo'].strip() == userId:
                        openid = wechat_user['openid']
                        temp_data = method.create_temp_data(order)
                        msg ={
                            'openid':openid,
                            'data':temp_data,
                            'app_id':app_id,
                            'secret':secret,
                            'access_token':access_token
                        }
                        # msg_list.append(msg)
                        thread = Thread(target=wx.send_temp,args=(msg,))
                        threads.append(thread)
                        thread.start()
            for t in threads:
                t.join()
            # if len(msg_list)>0:
            #     pool = ThreadPoolExecutor(len(msg_list)+1)
            #     for msg in msg_list:
            #         pool.submit(method.send_temp,msg)
        finally:
            last_one = orders[-1]['PurchSerial']
            caches['default'].set('wx_ikg_tempmsg_last_purchserial', last_one, 7 * 24 * 60 * 60)


def cron_gift_change_balance():
    # 1、查询消费记录
    prev_last_serial, orders = data.getGiftBalance()
    if len(orders) > 0:
        try:
            # 2、拼接wx_card_id
            for order in orders:
                qs_card = GiftCardCode.objects.values('wx_card_id').filter(code=order['CardNo']).first()
                order['wx_card_id'] = qs_card['wx_card_id']

            access_token = caches['default'].get('wx_kgcs_access_token', '')
            if not access_token:
                wx.get_access_token('kgcs', consts.KG_APPID, consts.KG_APPSECRET)

            threads = []
            for o in orders:
                thread = Thread(target=giftcard.change_balance,args=(o,access_token,))
                threads.append(thread)
                thread.start()
            for t in threads:
                t.join()

            this_last_serial = orders[-1]['PurchSerial']

            if prev_last_serial:
                now = datetime.datetime.now()
                GiftBalanceChangeLog.objects.filter(last_serial=prev_last_serial) \
                    .update(last_serial=this_last_serial,create_time=now.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                GiftBalanceChangeLog.objects.create(last_serial=this_last_serial)
            res_msg = 'ok'
        except Exception as e:
            print(e)
            LogWx.objects.create(type='2', errmsg=e, errcode='2')
            res_msg = e
    else:
        res_msg = 'no order'

    return HttpResponse(res_msg)

def cron_gift_compare_order():
    res = {}
    res['status'] = 0
    res_get = giftcard.get_Wx_order()
    if res_get['status'] == 0:
        offset = res_get['offset']
        total_count = res_get['total_count']
        wx_orders = res_get['wx_orders']
        data.local_save_gift_order(wx_orders)

        if total_count > (offset + 1) * 100:
            gift_compare_order(offset + 1)

    else:
        LogWx.objects.create(type='0', errmsg='cron_gift_compare_order_fail', errcode='0')
        return HttpResponse('fail')
    return HttpResponse('ok')



def gift_compare_order(offset=0):
    res = {}
    res['status'] = 0
    res_get = giftcard.get_Wx_order(offset)
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

def cron_shop_order_sign():
    save_time = datetime.date.today()+datetime.timedelta(-1)
    res = ShopOrder.objects.filter(save_time__lte=save_time,status='7').update(status='8')
    print('cron_shop_order_sign update rows:'+res)