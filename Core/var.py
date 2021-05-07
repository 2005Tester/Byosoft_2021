import logging
# global variables to track test progress etc
_global_var = {
    'current_test': '',
    'num_pass': 0,
    'num_fail': 0,
    'num_skip': 0,
    'log_dir': '.',
    'serial_log': ''
}


def _init():
    global _global_var


def set(key, value):
    logging.debug("Setting global variable")
    if key in _global_var:
        _global_var[key] = value
        return True
    else:
        raise Exception("Key: {0} not exist in global variable dict.".format(key))


def get(key, defValue=None):
    try:
        return _global_var[key]
    except KeyError:
        logging.error("Key: {0} not exist in global variable dict.".format(key))


# increace value by 1
def increase(key):
    logging.debug("Increase {0} by 1.".format(key))
    if (key in _global_var and isinstance(_global_var[key], int)):
        _global_var[key] += 1
    else:
        raise Exception("Key: {0} not exist or incorrect type.".format(key))


# decreace value by 1
def decrease(key):
    logging.debug("Decrease {0} by 1.".format(key))
    if (key in _global_var and isinstance(_global_var[key], int)):
        _global_var[key] -= 1
    else:
        raise Exception("Key: {0} not exist or incorrect type.".format(key))


def get_all():
    return _global_var
