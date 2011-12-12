
import twistymud.mixed

def mix_classes(name,base,mixin):
    if hasattr(twistymud.mixed,name):
        raise Exception("Mixed class already exists named {0}".format(name))
    class New(mixin,base):
        pass
    New.__name__ = name
    setattr(twistymud.mixed,name,New)
    New.__module__ = twistymud.mixed.__name__
    return New

