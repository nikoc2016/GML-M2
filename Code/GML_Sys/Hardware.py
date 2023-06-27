import math
import subprocess
import threading
import pythoncom
import wmi


class Hardware:
    def __init__(self):
        self.snapshot_result = None
        self.wmi_loading_thread = ThreadWmi()
        self.wmi_loading_thread.start()
        self.snapshot_check_timer = threading.Timer(1, self.check_loaded)
        self.snapshot_check_timer.start()

    def check_loaded(self):
        if self.wmi_loading_thread.done:
            self.snapshot_result = self.wmi_loading_thread.snapshot_result
            self.wmi_loading_thread = None
            self.snapshot_check_timer = None
            print("Hardware::Async Snapshot Loaded.")
        else:
            self.snapshot_check_timer = threading.Timer(1, self.check_loaded)
            self.snapshot_check_timer.start()


class ThreadWmi(threading.Thread):

    def __init__(self):
        super(ThreadWmi, self).__init__()
        self.snapshot = None
        self.snapshot_result = None
        self.done = False

    def run(self):
        pythoncom.CoInitialize()
        self.snapshot = wmi.WMI()
        self.snapshot_result = self.get_snapshot()
        pythoncom.CoUninitialize()
        self.done = True

    def get_cpus(self):
        cpu_data = []
        cpus = self.snapshot.Win32_Processor()
        for cpu in cpus:
            try:
                cpu_data.append(
                    {
                        "cpu_name": cpu.Name,
                        "cpu_serial": cpu.ProcessorId,
                        "cpu_core": cpu.NumberOfCores
                    }
                )
            except Exception as e:
                print(self.skip_str % (
                        "CPU (%s,%s,%s) %s" % (str(cpu.Name),
                                               str(cpu.ProcessorId),
                                               str(cpu.NumberOfCores),
                                               str(e))
                ))

        return cpu_data

    def get_ram(self):
        ram_in_gb = 0
        for i in self.snapshot.Win32_ComputerSystem():
            try:
                ram_in_gb += math.ceil(float(i.TotalPhysicalMemory) / (1024 ** 3))
            except Exception as e:
                print(self.skip_str % (
                        "RAM (%s) %s" % (str(i.TotalPhysicalMemory),
                                         str(e))
                ))

        return ram_in_gb

    def get_mboard(self):
        main_boards = []
        for board_id in self.snapshot.Win32_BaseBoard():
            try:
                mboard_info = {
                    "mboard_id": board_id.SerialNumber,
                    "mboard_name": board_id.Product,
                    "mboard_mfr": board_id.Manufacturer,
                }

                # If mboard_id is " " or "To be filled by O.E.M."， OVERRIDE
                if " " in mboard_info["mboard_id"]:
                    mboard_info["mboard_id"] = subprocess.check_output('wmic csproduct get uuid').split('\n')[1].strip()

                main_boards.append(mboard_info)
            except Exception as e:
                print(self.skip_str % (
                        "MBOARD (%s,%s,%s) %s" % (str(board_id.SerialNumber),
                                                  str(board_id.Product),
                                                  str(board_id.Manufacturer),
                                                  str(e))
                ))
        return main_boards

    def get_hdrive(self):
        hard_drives = []
        for hard_drive_object in self.snapshot.Win32_DiskDrive():
            try:
                hard_drives.append({
                    "hdrive_id": hard_drive_object.SerialNumber.strip(),
                    "hdrive_name": hard_drive_object.Caption,
                    "hdrive_size_in_GB": int(int(hard_drive_object.Size) // (1000 ** 3)),
                })
            except Exception as e:
                print(self.skip_str % (
                        "HDRIVE (%s,%s,%s) %s" % (str(hard_drive_object.SerialNumber),
                                                  str(hard_drive_object.Caption),
                                                  str(hard_drive_object.Size),
                                                  str(e))
                ))
        return hard_drives

    def get_vcard(self):
        try:
            return self.snapshot.Win32_VideoController()[0].Caption
        except Exception as e:
            print(self.skip_str % (
                    "VCARD (%s) %s" % (str(self.snapshot.Win32_VideoController()),
                                       str(e))
            ))
        return None

    def get_mac(self):
        mac_addr = None
        not_match_keywords = ["WAN Miniport", "VMware", "Bluetooth"]

        for record in self.snapshot.WIN32_NetworkAdapter():
            try:
                # For each Network Adapter
                if record.MACAddress:
                    # Check if correct Network Adapter
                    match = True
                    for keyword in not_match_keywords:
                        if keyword.lower() in str(record.Caption).lower():
                            match = False
                            break
                    # Found Mac
                    if match:
                        mac_addr = str(record.MACAddress).replace(":", ".").lower()
            except Exception as e:
                print(self.skip_str % (
                        "NET ADAPTER (%s) %s" % (str(record.Caption),
                                                 str(e))
                ))
        return mac_addr

    def get_snapshot(self):
        return {
            "cpus": self.get_cpus(),
            "mboards": self.get_mboard(),
            "hdrives": self.get_hdrive(),
            "vcard": self.get_vcard(),
            "ram": self.get_ram(),
            'mac': self.get_mac()
        }
