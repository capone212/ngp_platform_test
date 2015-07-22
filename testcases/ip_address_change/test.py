import os
import shlex
import logging
import sys
import time
import psutil
import systemutils
import support
import shutil

from random import randint

from itexceptions import ItGeneralError
from itexceptions import ItBaseException
from systemutils import get_ngp_process_list
from systemutils import exec_command
from systemutils import wait_process_to_finish
from systemutils import wait_ngp_to_start

from definitions import IP_ADDRESS_CHANGE_NIC_ID
from definitions import TEST_SUPPORT_ROOT_DIRR

_logger = logging.getLogger("ap_address_change")

MAX_TEST_CYCLES = 100;
MAX_WAIT_TIME_SECONDS = 90
CHECK_INTERVAL_SECONDS = 3
MAX_WAIT_TIME_AFTER_START = 25


def init_debug_logger(logger):
    # Set Log level
    logger.setLevel(logging.DEBUG)
    #Set handler11111
    log_handler = logging.StreamHandler(sys.stdout)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)


def simulate_ipaddress_change():
    # wmic path win32_networkadapter where index=14 call enable
    NIC_ID = IP_ADDRESS_CHANGE_NIC_ID
    exec_command("wmic path win32_networkadapter where index=%s call enable" % NIC_ID)
    time.sleep(5);
    exec_command("wmic path win32_networkadapter where index=%s call disable" % NIC_ID)


# system passed test case 
TC_STATUS_OK = "PASSED"
# system did not passed the test
TC_STATUS_FAILED = "FAILED"
# test case execution terminated on error 
TC_STATUS_ERROR = "ERROR"

def run_once():
    #clean
    _logger.info("Starting ngp...")
    systemutils.start_ngp_service(_logger)
    _logger.info("Waiting random time...")
    
    # TODO: random time out
    #time.sleep(randint(0, MAX_WAIT_TIME_AFTER_START));
    time.sleep(60);

    _logger.info("Getting current ngp process list...")
    process_list_orig = get_ngp_process_list()
    if (not process_list_orig):
        _logger.warn("Current ngp process list empty!")
        return TC_STATUS_FAILED
    _logger.info("Simulate ip address table change...")
    simulate_ipaddress_change()
    _logger.info("Wait ngp processes to exit...")
    remain = wait_process_to_finish(MAX_WAIT_TIME_SECONDS,
        CHECK_INTERVAL_SECONDS, process_list_orig)
    if remain :
        _logger.warn("Current processes persists %s", remain)
        return TC_STATUS_FAILED
    _logger.info("Wait ngp services to start again...")
    started = wait_ngp_to_start(MAX_WAIT_TIME_SECONDS, CHECK_INTERVAL_SECONDS)
    if not started:
        _logger.warn("NGP did not start after %s seconds", MAX_WAIT_TIME_SECONDS)
        return TC_STATUS_FAILED
    # exec command
    return TC_STATUS_OK

def get_folder_for_task(task_no):
    task_folder = TEST_SUPPORT_ROOT_DIRR + "/" +str(task_no)
    shutil.rmtree(task_folder, ignore_errors=True)
    time.sleep(0.5)
    os.makedirs(task_folder)
    return task_folder


def run_test():
    for i in range(0, MAX_TEST_CYCLES):
        support.clean()
        _logger.info("-"*80)
        _logger.info("Run test #%s", i)
        result = "undefined"
        try:
            result = run_once()
        except Exception, e:
            result = TC_STATUS_ERROR
        if (support.is_crashes_exists()):
            _logger.warn("Found crash dumps after test cycle!")
            #result = TC_STATUS_ERROR
        if result != TC_STATUS_OK:
            support.collect_support_info(
                get_folder_for_task(i))
        _logger.info("Test #%s finished. Status = %s", i, result)


if __name__ == "__main__":
    init_debug_logger(_logger)
    run_test()
