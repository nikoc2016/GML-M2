import argparse
import errno
import os
import tempfile

import GML

# Static Classes
from GML_Sys.Version import Version as GML_Version
from GML_Sys.Hardware import Hardware as GML_Hardware
from GML_Sys.Datetime import GML_Datetime
from GML_Sys.LaunchExternal import LaunchExternal


# Methods
def configure_paths(enforce_dev_mode=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-dev', "--dev_mode", action='store_true', default=False,
                        dest='dev_mode',
                        help='Using dev_mode directories.')
    parsed_args = parser.parse_args()

    # Dev
    if parsed_args.dev_mode or enforce_dev_mode:
        GML.app_dev_mode = True
        GML.app_full_name += "[DEV]"
    else:
        GML.app_dev_mode = False

    # Dirs & Paths
    GML.app_version = GML_Version(GML.app_version)
    GML.dir_my_doc = os.path.join(os.path.expanduser('~'), 'Documents', GML.app_short_name)
    GML.dir_temp = os.path.join(tempfile.gettempdir(), GML.app_short_name)
    GML.app_lock_path = os.path.join(GML.dir_my_doc, GML.app_short_name + ".lock")

    # Make Dirs
    try:
        os.makedirs(GML.dir_my_doc)
    except:
        pass
    try:
        os.makedirs(GML.dir_temp)
    except:
        pass


def lock_multi_instance():
    try:
        os.remove(GML.app_lock_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            print("Sys::lock_multi_instance()::Another GML is running")
            if GML.app_compiled:
                print("Sys::lock_multi_instance()::Awaking existing GML [NOT IMPLEMENTED]")
                # with open(GML_Globals.mydoc_awakeFile_path, "w"):
                #     pass
            return False

    try:
        GML.app_lock_handle = open(GML.app_lock_path, "w")
    except Exception as e:
        print('Sys::lock_multi_instance()::Lock Failure::' + str(e) + '')
        return False

    print("Sys::lock_multi_instance()::GML is now locked.")
    return True
