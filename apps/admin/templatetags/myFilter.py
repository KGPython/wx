# -*-  coding:utf-8 -*-
__author__ = ''
__date__ = '2017/6/23 9:46'
import time

from django import template

register = template.Library()

@register.filter('range')
def to_list(value):
    return range(1, int(value)+1)

@register.filter('int')
def to_int(val):
    return int(val)


#加法：v1 + v2
@register.filter
def add(v1,v2):
    return float(v1) + float(v2)

#减法：v1 - v2
@register.filter
def subtract(v1,v2):
    return float(v1) - float(v2)

#乘法：v1 * v2
@register.filter
def multiply(v1,v2):
    return float(v1) * float(v2)

#除法：v1 / v2
@register.filter
def divide(v1,v2):
    return float(v1) / float(v2)

 #取余：v1 % v2
@register.filter
def remainder(v1,v2):
    return float(v1) % float(v2)

@register.filter
def toDate(data):
    x = time.localtime(float(data))
    return time.strftime('%y-%m-%d %H:%M:%S', x)

