import subprocess
import os
import shlex
import logging
import sys
import time
import psutil

from itexceptions import ItGeneralError
from itexceptions import ItBaseException

_logger = logging.getLogger("ap_address_change")

def init_debug_logger(logger):
    # Set Log level
    logger.setLevel(logging.DEBUG)
    #Set handler11111
    log_handler = logging.StreamHandler(sys.stdout)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

def exec_command(command_line, env_vars=os.environ.copy()):
    args = shlex.split(command_line)
    try:
        return subprocess.check_output(args, env=env_vars, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        raise ItGeneralError("Error occurred while executing command: %s output: %s" % (err, err.output))


def start_ngp():
    try:
        return exec_command("net start ngp_host_service")
    except ItBaseException as exc:
        _logger.info("start_ngp returned error %s", repr(exc))

def get_ngp_process_list():
    ngp_app_names = [u'AppHost.exe', u'AppHostSvc.exe']
    return [p for p in psutil.process_iter() if p.name() in ngp_app_names]


def runTestOnce():
    #clean
    start_ngp()
    time.sleep(5);
    print is_ngp_started()

if __name__ == "__main__":
    init_debug_logger(_logger)
    runTestOnce()
