import logging
import subprocess
import time
import re

# function library to hold platform indepedent operations, to simplify test case developemnt.


# check whether SUT is online
def ping_sut(ip, timeout):
    logging.info("Test network connection...")
    ping_cmd = 'ping {0}'.format(ip)
    start_time = time.time()
    while True:
        p = subprocess.Popen(args=ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        now = time.time()
        time_spent = (now - start_time)
        if 'TTL=' in stdoutput.decode('gbk'):
            logging.info("SUT is online.")
            return True
        if time_spent > timeout:
            logging.error("Lost SUT for %s seconds, check the network connection" % time_spent)
            return False


# Verify a bunch of messages (list) in a captured log (str)
def verify_msgs_in_log(msg_list, captured_log):
    result = True
    if not captured_log:
        logging.error("Nothing in input log")
        return
    for msg in msg_list:
        if re.search(msg, captured_log):
            logging.info("Verified: {0}".format(msg))
        else:
            logging.info("Not verified: {0}".format(msg))
            result = False
    return result
