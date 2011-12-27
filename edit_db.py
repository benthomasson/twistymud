#!/usr/bin/env python

from twistymud.settings import DB_NAME

import readline
import cmd

from twistymud.persist import Persistence
import twistymud.persist


class EditDb(cmd.Cmd):

    intro = 'Edit the DB'
    prompt = '>'
    keys = []

    def emptyline(self):
        print "\n".join(twistymud.persist.persistence.db.keys())

    def default(self,line):
        line = line.strip()
        if line in twistymud.persist.persistence.db:
            o =  twistymud.persist.persistence.db[line]
            if hasattr(o,'__dict__'):
                eo = EditDBObject()
                eo.obj = o
            else:
                eo = EditDBValue()
            eo.name = line
            eo.prompt = "{0}>".format(line)
            try:
                eo.cmdloop()
            except KeyboardInterrupt:
                print "Done editing {0}".format(line)
                pass

    def completenames(self,current,full,*ignore):
        return filter(lambda x: x.startswith(current),self.keys)

    def do_EOF(self,line):
        raise KeyboardInterrupt()



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
                print "Done editing {0}.{1}".format(self.name,line)

class EditObjectValue(cmd.Cmd):

    def do_EOF(self,line):
        raise KeyboardInterrupt()

    def emptyline(self):
        print getattr(self.obj,self.name)

    def do_seti(self,line):
        setattr(self.obj,self.name,int(line))

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

def main():
    twistymud.persist.persistence = Persistence(DB_NAME)
    for id in twistymud.persist.persistence.db.keys():
        print id
    edit = EditDb()
    edit.keys = twistymud.persist.persistence.db.keys()
    try:
        edit.cmdloop()
    except KeyboardInterrupt:
        print "Done editing db"
    print "\Persisting..."
    twistymud.persist.persistence.syncAll()
    twistymud.persist.persistence.close()
    print "\nDone"

if __name__ == "__main__":
    main()
