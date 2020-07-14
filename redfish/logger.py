import logging
from logging import handlers

class Logger(object):
    log_level = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        log_format = logging.Formatter(fmt)
        self.logger.setLevel(self.log_level.get(level))
        write2file = logging.StreamHandler()
        write2file.setFormatter(log_format) 
        print2screen = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')
        print2screen.setFormatter(log_format)
        self.logger.addHandler(write2file) 
        self.logger.addHandler(print2screen)