import fudge

class ShuntMixin(object):
    def __patch_method__(self, method_name, expects_call=True):
        class_name = self.__class__.__name__
        fake_method = fudge.Fake('%s.%s' % (class_name, method_name))
        if expects_call:
            fake_method.expects_call()
        else:
            fake_method.is_callable()
        setattr(self, method_name, fake_method)
        return fake_method

def shunt_class(Klass):
    """Creates a shunt for any object"""
    class ShuntClass(Klass, ShuntMixin):
        pass
    ShuntClass.__name__ = '%sShunt' % Klass.__name__
    return ShuntClass
