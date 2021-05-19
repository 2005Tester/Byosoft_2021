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


# capture the section of serial log from start_str to end_str
def cut_log(serial, start_str, end_str, duration=20, timeout=120, step=30):
    logging.info(f"Capture serial output from: '{start_str}' to '{end_str}'")
    data_saved = ""
    cut_begain = 0
    start_time = time.time()
    while True:
        if serial.session.in_waiting:
            tmpdata = ""
            for i in range(step):  # read multi lines for speed up
                tmp = serial.session.readline().decode("utf-8")  # read one line to avoid keywords split
                tmpdata += tmp
            clndata = serial.cleanup_data(tmpdata)
            if re.search(start_str, clndata):  # start_str found
                cut_begain = time.time()
                logging.info(f"Start string found: {start_str}")
            if cut_begain:
                if time.time()-cut_begain < duration:  # cache serial output
                    data_saved += clndata
                if re.search(end_str, clndata):  # cache last tmpdata
                    logging.info(f"End string found: {end_str}")
                    if not re.search(end_str, data_saved):  # in case of first tmpdata contains start_str and end_str
                        data_saved += clndata
                    return data_saved
                if time.time()-cut_begain > duration:  # duration timeout
                    logging.info(f"Start string found but missing end string: duration timeout for {duration}s")
                    return data_saved
        if time.time() - start_time > timeout:  # nothing found, timeout limit
            logging.info(f"Nothing found, timeout for {timeout}s")
            return data_saved
