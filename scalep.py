#!/usr/bin/env python

from twistymud.persist import P, Persistent

if __name__ == "__main__":

    for i in xrange(10000000):
        o = Persistent()
        o.id = i
        p = P(o)
    print len(P.instances)

