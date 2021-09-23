import logging

# add html style in logging message, style is defined in html report template


def _formatter(text, type):
    if type == "fail":
        return "<span class=\"text-danger\">{0}</span>".format(text)
    elif type == "success":
        return "<span class=\"text-info\">{0}</span>".format(text)
    elif type == "warning":
        return "<span class=\"text-warning\">{0}</span>".format(text)
    elif type == "info":
        return "<span class=\"text-success\">{0}</span>".format(text)
    else:
        return text


# Red text in html report for test failures
def fail(text):
    logging.info(_formatter(text, "fail"))


# Green text in html report for passed tests
def success(text):
    logging.info(_formatter(text, "success"))


# Yellow text in html report for warnings
def warning(text):
    logging.info(_formatter(text, "warning"))


# Blue text in html report for information
def info(text):
    logging.info(_formatter(text, "info"))