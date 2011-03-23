#!/usr/bin/env python
#-*- coding: utf8 -*-


class BaseFilter(object):
    
    def __init__(self):
        pass
    
    def before(self, context):
        pass
    
    def after(self, context):
        pass