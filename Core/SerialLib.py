import re
import time
import logging


# Monitor serial output and check whether specified message exists
def is_msg_present(serial, msg, delay=150, cleanup=True):
    pw_prompt = None
    pw = None
    return serial.is_msg_present_general(msg, delay, pw_prompt, pw, cleanup)


# Monitor serial output and check whether specified message not exist
def is_msg_not_present(serial, msg1, msg2):
    return serial.is_msg_not_present(msg1, msg2)


# Monitor serial output and check whether specified messages in a list exist
def is_msg_list_present(serial, msg_list, delay=10):
    return serial.waitStrings(msg_list, delay)


# send keys with delay
def send_keys_with_delay(serial, keys, delay=1):
    logging.info("Sending keys...")
    for key in keys:
        serial.send_keys(key)
        time.sleep(delay)


# send a key from serial port
def send_key(serial, key):
    logging.info("Sending Key...")
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


# Receive data from serial port
def recv_data(serial, size=1024):
    return serial.receive_data(size)


# Clean serial output buffer
def clean_buffer(serial):
    serial.data = ""


# capture the section of serial log from start_str to end_str
def cut_log(serial, start_str, end_str, duration=20, timeout=120):
    return serial.cut_log(start_str, end_str, duration, timeout)
