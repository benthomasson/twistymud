#!/usr/bin/env python

from twistymud.mudserver import Mud

if __name__ == "__main__":
    mud = Mud.getInstance()
    mud.run()
