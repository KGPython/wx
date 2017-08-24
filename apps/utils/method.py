import random,hashlib,time

from django.core.cache import caches

from utils import db,consts

def createNonceStr(length = 16):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    str = ""
    for i in range(0,length):
        _index = random.randint(0, len(chars) - 1)
        str += chars[_index:_index+1]
    return str


def getShopName(id):
    """
    门店code==》门店名称
    :param id:
    :return:
    """
    shopDict = caches['default'].get('base_shopDict', '')
    if not shopDict:
        conn = db.getMysqlConnection(
            consts.DB_SERVER_18,
            consts.DB_PORT_18,
            consts.DB_USER_18,
            consts.DB_PASSWORD_18,
            consts.DB_DATABASE_18
        )
        sql = "SELECT Shopcode,Shopnm FROM bas_shop WHERE enable = 1"
        cur = conn.cursor()
        cur.execute(sql)
        shops = cur.fetchall()

        conn2 = db.getMysqlConnection(
            consts.DB_SERVER_18,
            consts.DB_PORT_18,
            consts.DB_USER_18,
            consts.DB_PASSWORD_18,
            'kgscm_ts'
        )
        sql2 = "SELECT Shopcode,Shopnm FROM bas_shop WHERE enable = 1"
        cur2 = conn2.cursor()
        cur2.execute(sql2)
        shops2 = cur.fetchall()

        shops = shops + shops2

        shopDict = {shop['Shopcode']: shop['Shopnm'].strip() for shop in shops}
        caches['default'].set('base_shopDict', shopDict, 60 * 60 * 12)

    return shopDict.get(id,id)


def get_ip(request):
    """
    获取ip
    :param request:
    :return:
    """
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


def md5(data):
    """
    md5加密
    :param data:
    :return:
    """
    md5 = hashlib.md5()
    if data:
        md5.update(data.encode(encoding='utf-8'))
    return md5.hexdigest()


def getTimeStamp(str):
    return time.mktime(time.strptime(str, '%Y-%m-%d %H:%M:%S'))


def create_temp_data(order):
    data = {}
    # 模版数据字典
    data['first'] = {
        "value": "宽广会员专享优惠券-爱宽广微信小程序",
        "color": "#173177"
    }
    data['keyword1'] = {
        "value": order['CardNo'].strip(),
        "color": "#173177"
    }
    data['keyword2'] = {
        "value": getShopName(order['shopID']) + "(" + order['Branchno'] + "/" + str(order['ListNO']) + ")",
        "color": "#173177"
    }
    data['keyword3'] = {
        "value": str(float('%.2f' % order['PayMoney'])),
        "color": "#173177"
    }
    data['remark'] = {
        "value": "消费日期：" + order['PurchDateTime'].strftime("%Y-%m-%d %H:%M:%S") + ' \n详询4001110314',
        "color": "#173177"
    }

    return data


def createResult(errcode,errmsg,data=None):
    return {
        'errcode':errcode,
        'errmsg':errmsg,
        'data':data,
    }