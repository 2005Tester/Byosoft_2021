import datetime
import os


def gen_config(log_dir):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log = "test.log"
    log_file = os.path.join(log_dir, log)
    logger_config = {
        'version': 1,
        'formatters': {
            'normal': {
                'format': '%(asctime)s %(levelname)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'normal',
                'level': 'INFO',
            },
            'file': {
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'normal',
                'filename': log_file,
                'mode': 'a',
                'level': 'INFO',
            },

        },
        'loggers': {
            'console': {'level': 'DEBUG',
                        'handlers': ['console','file'],
                        },
            'requests.packages.urllib3.connectionpool': {'level': 'ERROR'},

        },
        'root': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        }
    }

    return logger_config
