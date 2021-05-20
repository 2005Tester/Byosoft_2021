import logging
import subprocess
import time

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
