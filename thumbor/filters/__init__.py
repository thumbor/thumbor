#!/usr/bin/env python
#-*- coding: utf8 -*-


class BaseFilter(object):
    
    def __init__(self, context):
        self.context = context
    
    def before(self):
        pass
    
    def after(self):
        pass