#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

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
                'level': 'DEBUG',
            },

        },
        'loggers': {
            'console': {'level': 'INFO',
                        'handlers': ['console','file'],
                        },
            'requests.packages.urllib3.connectionpool': {'level': 'ERROR'},

        },
        'root': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        }
    }

    return logger_config
