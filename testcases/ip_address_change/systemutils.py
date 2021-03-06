import os
import subprocess
import shlex
import psutil
import time


from definitions import NGP_SHELL_PATH
from itexceptions import ItGeneralError
from itexceptions import ItBaseException

def exec_command(command_line, env_vars=os.environ.copy()):
    args = shlex.split(command_line)
    try:
        return subprocess.check_output(args, env=env_vars, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        raise ItGeneralError("Error occurred while executing command: %s output: %s" % (err, err.output))

def start_ngp_service(logger):
    try:
        return exec_command("net start ngp_host_service")
    except ItBaseException as exc:
        logger.info("start_ngp returned error %s", repr(exc))

def stop_ngp_service(logger):
    try:
        return exec_command("net stop ngp_host_service")
    except ItBaseException as exc:
        logger.info("stop_ngp returned error %s", repr(exc))

def check_ngp_hostagent(logger, ipaddress):
    try:
        exec_command(NGP_SHELL_PATH + " -ORBDefaultInitRef corbaloc:iiop:1.2@%s:49999 hostagent info" % ipaddress)
        return True
    except ItBaseException as exc:
        logger.info("check_ngp_hostagent error %s", repr(exc))
        return False

def get_ngp_process_list():
    try:
        ngp_app_names = [u'AppHost.exe', u'AppHostSvc.exe']
        return [p for p in psutil.process_iter() if p.name() in ngp_app_names]
    except Exception, e:
        return get_ngp_process_list()

# Returns list of alive process's PID
def get_process_alive(process_list):
    try:
        crrent_list = set(map(lambda x: x.pid ,psutil.process_iter()))
        list_to_test = set(map(lambda x: x.pid ,process_list))
        return set.intersection(crrent_list, list_to_test)
    except Exception as ex:
        return get_process_alive(process_list)

# Returns set of alive process after wait
def wait_process_to_finish(max_wait_sec, check_intvl_sec, process_list):
    alive_process = set()
    for i in range(0, max_wait_sec, check_intvl_sec):
        alive_process = get_process_alive(process_list)
        if (not alive_process):
            break;
        time.sleep(check_intvl_sec);
    return alive_process

# Return false if ngp processes still persists after wait.
def wait_ngp_to_start(max_wait_sec, check_intvl_sec):
    for i in range(0, max_wait_sec, check_intvl_sec):
        process_list = get_ngp_process_list()
        if (len(process_list) > 3):
            return True;
        time.sleep(check_intvl_sec);
    return False

def kill_ngp_processes():
    try:
        for p in get_ngp_process_list():
            try:
                p.kill()
            except Exception as e:
                pass
    except Exception as e:
        kill_ngp_processes()