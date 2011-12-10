#!/usr/bin/env python

from twisted.internet import reactor
import time


def printTime():
    print "Current time is", time.strftime("%H:%M:%S")
    reactor.callLater(1,printTime)

def stopReactor():
    print "Stopping reactor"
    reactor.stop()

reactor.callLater(1,printTime)

print "Running the reactor..."
reactor.run()
print "Reactor stopped"



