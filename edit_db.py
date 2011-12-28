#!/usr/bin/env python

from twistymud.settings import DB_NAME

import readline
import cmd

from twistymud.persist import Persistence
import twistymud.persist


def parseBool(b):
    b = b.lower()
    return b not in ['false','f','no','null']


class EditDb(cmd.Cmd):

    keys = []

    def emptyline(self):
        print "\n".join(self.keys)

    def default(self,line):
        line = line.strip()
        if line in twistymud.persist.persistence.db:
            o =  twistymud.persist.persistence.db[line]
            if hasattr(o,'__dict__'):
                eo = EditDBObject()
                eo.obj = o
                eo.prompt = "{0}({1})>".format(line,o.__class__.__name__)
            else:
                eo = EditDBValue()
                eo.prompt = "{0}>".format(line)
            eo.name = line
            try:
                eo.cmdloop()
            except KeyboardInterrupt:
                print "\nDone editing {0}".format(line)
                pass

    def completenames(self,current,full,*ignore):
        cmds = ['del','del_error']
        return filter(lambda x: x.startswith(current),cmds + self.keys)

    def do_EOF(self,line):
        raise KeyboardInterrupt()

    def do_del(self,line):
        name = line.strip()
        if name in twistymud.persist.persistence.db:
            del twistymud.persist.persistence.db[name]
            self.keys = sorted(twistymud.persist.persistence.db.keys())
            print "Deleted {0}".format(name)
        else:
            print "No objects named {0}".format(name)

    def do_del_error(self,line):
        for name in self.keys:
            try:
                twistymud.persist.persistence.db[name]
            except Exception:
                del twistymud.persist.persistence.db[name]
        self.keys = sorted(twistymud.persist.persistence.db.keys())


class EditDBObject(cmd.Cmd):

    def do_EOF(self,line):
        raise KeyboardInterrupt()

    def emptyline(self):
        for name, value in self.obj.__dict__.iteritems():
            print "{0:20} {1}".format(name,value)

    def completenames(self,current,full,*ignore):
        return filter(lambda x: x.startswith(current),self.obj.__dict__)

    def default(self,line):
        line = line.strip()
        if hasattr(self.obj,line):
            eov = EditObjectValue()
            eov.obj = self.obj
            eov.name = line
            eov.prompt = "{0}.{1}>".format(self.name,line)
            try:
                eov.cmdloop()
            except KeyboardInterrupt:
                print "\nDone editing {0}.{1}".format(self.name,line)

class EditObjectValue(cmd.Cmd):

    def do_EOF(self,line):
        raise KeyboardInterrupt()

    def emptyline(self):
        print getattr(self.obj,self.name)

    def do_seti(self,line):
        setattr(self.obj,self.name,int(line))

    def do_seti(self,line):
        setattr(self.obj,self.name,int(line))

    def do_setl(self,line):
        setattr(self.obj,self.name,long(line))

    def do_setf(self,line):
        setattr(self.obj,self.name,float(line))

    def do_sets(self,line):
        setattr(self.obj,self.name,line)

    def do_setb(self,line):
        setattr(self.obj,self.name,parseBool(line))

class EditDBValue(cmd.Cmd):

    def do_EOF(self,line):
        raise KeyboardInterrupt()

    def emptyline(self):
        print twistymud.persist.persistence.db[self.name]

    def do_seti(self,line):
        twistymud.persist.persistence.db[self.name]=int(line)

    def do_setl(self,line):
        twistymud.persist.persistence.db[self.name]=long(line)

    def do_setf(self,line):
        twistymud.persist.persistence.db[self.name]=float(line)

    def do_sets(self,line):
        twistymud.persist.persistence.db[self.name]=line

    def do_setb(self,line):
        twistymud.persist.persistence.db[self.name]=parseBool(line)

def main():
    twistymud.persist.persistence = Persistence(DB_NAME)
    edit = EditDb()
    edit.prompt = DB_NAME + ">"
    edit.keys = sorted(twistymud.persist.persistence.db.keys())
    try:
        edit.cmdloop('Edit the DB {0}'.format(DB_NAME))
    except KeyboardInterrupt:
        print "\nDone editing db {0}".format(DB_NAME)
    print "\Persisting..."
    twistymud.persist.persistence.syncAll()
    twistymud.persist.persistence.close()
    print "\nDone"

if __name__ == "__main__":
    main()
