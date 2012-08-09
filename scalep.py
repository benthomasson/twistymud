#!/usr/bin/env python

from persist import P, Persistent

import time

if __name__ == "__main__":

    for i in xrange(3000000):
        o = Persistent()
        o.id = i
        p = P(o)
    print len(P.instances)

    time.sleep(10000)
