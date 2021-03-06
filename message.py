#!/usr/bin/env python

import unittest

from persist import getP

class Message(object):

    def __init__(self,type,**kwargs):
        self.type = type
        self.dict = {'_exclude':[]}
        self.dict.update(kwargs)

    def __str__(self):
        return "message: %s" % self.type

    def __repr__(self):
        return self.__str__()

class Channel(object):

    def __init__(self,id=None):
        self.listeners = {}
        self.id = id

    def addListener(self,listener):
        self.listeners[listener.id] = getP(listener)

    def removeListener(self,listener):
        if listener.id in self.listeners:
            del self.listeners[listener.id]

    def sendMessage(self,type,**kwargs):
        message = Message(type,**kwargs)
        self._sendMessage(message)

    def _sendMessage(self,message):
        _exclude = message.dict['_exclude']
        for id in self.listeners.copy().keys():
            listener = self.listeners[id]
            listener = listener()
            if listener and listener not in _exclude:
                listener.receiveMessage(message)
            elif not listener:
                del self.listeners[id]


class RepeaterMixin(object):

    def receiveMessage(self,message):
        self._sendMessage(message)
