"""
Various Data Test Tools
"""
import random

NUMBER = "0123456789"
SYMBOL = """!@#$%^&*()_+=-[]\;',./{}|:"<>?~`"""
ALPHA_LOWER = "abcdefghijklmnopqrstuvwxyz"
ALPHA_UPPER = ALPHA_LOWER.upper()
ALL_ALPHA = ALPHA_LOWER + ALPHA_UPPER
ALPHA_NUMERIC = ALL_ALPHA + NUMBER
ALL_CHARS = SYMBOL + ALPHA_NUMERIC

def random_string(length, chars=ALL_CHARS):
    """Generates a random string of length"""
    array = []
    for i in xrange(length):
        c = random.choice(chars)
        array.append(c)
    return "".join(array)

def dict_to_object(d):
    return type('DictAsObject', (object,), d)
    
