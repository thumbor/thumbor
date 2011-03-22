#!/usr/bin/env python
#-*- coding: utf8 -*-

def real_import(name):
    if '.'  in name:
        return reduce(getattr, name.split('.')[1:], __import__(name))
    return __import__(name)
