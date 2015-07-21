import os
import psutil
import zipfile
import shutil
import time

from systemutils import exec_command
from systemutils import get_ngp_process_list
from systemutils import kill_ngp_processes

from definitions import PROC_DUMP_PATH
from definitions import AXXON_NEXT_LOG_DIR

from itexceptions import ItGeneralError
from itexceptions import ItBaseException

def create_memory_dump_for(p, support_path):
    # procdump -ma 4572 dump_file.dmp
    #-accepteula -ma
    command = "{procdump} -accepteula -ma {pid} {folder}/{name}_{pid}.dmp".format(procdump = PROC_DUMP_PATH,
        pid = p.pid, folder=support_path, name = p.name())
    print command
    try:
        exec_command(command)
    except ItBaseException as exc:
        pass

def create_dumps_of_live_process(support_path):
    for p in get_ngp_process_list():
        create_memory_dump_for(p, support_path)

def zipdir(path, zipFile):
    zipf = zipfile.ZipFile(zipFile, 'w', allowZip64=True)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))

def collect_support_info(support_path):
    create_dumps_of_live_process(support_path)
    zipdir(AXXON_NEXT_LOG_DIR, os.path.join(support_path, "Logs.zip"))


def clean():
    kill_ngp_processes()
    time.sleep(1)
    #clen dirrectories
    shutil.rmtree(AXXON_NEXT_LOG_DIR, ignore_errors=True)
    time.sleep(1)
    os.makedirs(AXXON_NEXT_LOG_DIR)


def is_crashes_exists():
    for root, dirs, files in os.walk(AXXON_NEXT_LOG_DIR):
        for file in files:
            if file.endswith(".dmp"):
                return True
    return False