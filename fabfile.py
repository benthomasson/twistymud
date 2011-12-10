#!/usr/bin/env python

from fabric.api import local, settings

def save():
    local('git commit -a -m "saving"')
    push()

def push():
    pull()
    local('git push')

def pull():
    local('git pull --rebase')

def status():
    local('git status')
