# -*- coding: utf-8 -*-
# Source: http://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing

from multiprocessing import Value, Lock

class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()

    def increment(self, inc=1):
        with self.lock:
            self.val.value += inc

    def value(self):
        with self.lock:
            return self.val.value