import logging.config
from Common import LogConfig
from Moc25 import updatebios
from Moc25 import Moc25Config


# Init log setting
log_dir = Moc25Config.LOG_DIR
log_format = LogConfig.gen_config(log_dir)
logging.config.dictConfig(log_format)
logging.getLogger("paramiko").setLevel(logging.WARNING)

if __name__ == '__main__':
    updatebios.get_test_image(Moc25Config.BINARY_DIR)

