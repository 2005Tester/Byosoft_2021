import logging
import subprocess
import time
import re
import os
import tarfile
from collections import Counter
from PIL import Image, ImageChops

# function library to hold platform indepedent operations, to simplify test case developemnt.


# check whether SUT is online
def ping_sut(ip, timeout):
    logging.info("Ping SUT: {0}...".format(ip))
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
            logging.error("Failed to ping SUT")
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


# Extract files from ".tar.gz" package
def uncompress_targz(targz_file, uncom_path):
    try:
        assert targz_file.endswith(".tar.gz"), f"Unsupported file ext: {targz_file}"
        name_ext = os.path.split(targz_file)[1]
        file_name = name_ext[:name_ext.find(".tar.gz")]
        uncom_path = os.path.join(uncom_path, file_name)
        tar = tarfile.open(targz_file)
        tar.extractall(path=uncom_path)
        return uncom_path
    except Exception as e:
        logging.error(e)
        logging.info(f"Exception: uncompress package {targz_file} fail")
        return False


# compare whether two images are the same
# "image_diff" save the difference as a picture if not same
# return True if they are same
def compare_images(image1, image2, image_diff=""):
    image_one = Image.open(image1)
    image_two = Image.open(image2)
    try:
        diff = ImageChops.difference(image_one, image_two)
        if diff.getbbox() is None:
            logging.info("Compare two images are the same")
            return True
        if image_diff:
            logging.info("Compare two images are different")
            diff.save(image_diff)
            return False
    except Exception as e:
        print(f"Compare image error：\n{e}")


# compare two items contains same values but ignore the sequence
def same_values(item_a, item_b):
    try:
        if Counter(item_a) == Counter(item_b):
            logging.debug("Values are same.")
            return True
        logging.debug("Values are different.")
        return False
    except Exception as e:
        logging.error(e)
