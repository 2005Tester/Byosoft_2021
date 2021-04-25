import time
import logging


# Monitor serial output and check whether specified message exists
def is_msg_present(serial, msg, delay=150):
    pw_prompt = None
    pw = None
    cleanup = True
    return serial.is_msg_present_general(msg, delay, pw_prompt, pw, cleanup)


# Monitor serial output and check whether specified message not exist
def is_msg_not_present(serial, msg1, msg2):
    return serial.is_msg_not_present(msg1, msg2)


# Monitor serial output and check whether specified messages in a list exist
def is_msg_list_present(serial, msg_list, delay=10):
    return serial.waitStrings(msg_list, delay)


# send keys with delay
def send_keys_with_delay(serial, keys, delay=1):
    logging.info("Sending keys:{0}".format(keys))
    for key in keys:
        serial.send_keys(key)
        time.sleep(delay)


# send a key from serial port
def send_key(serial, key):
    logging.info("Sending key:{0}".format(key))
    serial.send_keys(key)


# send a command from serial port, "\n" need to be added
def run_command(serial, command, msg):
    serial.run_command(command, msg)


# Send data from serial port
def send_data(serial, data):
    logging.info("Sending data:{0}".format(data))
    serial.send_data(data)


# Read serial output buffer
def read_buffer(serial):
    return serial.data
