# Update Log
# V1.0.1 -> Add mac address collection
# V1.0.2 -> Add date verification
# V1.0.3 -> Add close maya broadcast + Fixing 1.0.2 negative date bug + Fixing Unknown CHANNEL_ID crash bug
# V1.0.4 -> Collects CGT account, passwords
# V1.1.0 -> Port to GML V2

import time
import traceback

import psutil
from PySide2.QtCore import QThread
from NikoKit.NikoLib.NKDatabase import NKMySQLConnector
from GML_Runtime import GMLRuntime
from NikoKit.NikoLib import NKLogger
from datetime import datetime
from NikoKit.NikoStd.NKVersion import NKVersion

LOG_CHANNEL = "LegacySupport"


def log(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_OUT,
                                    log_context=context)


def log_warn(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_WARNING,
                                    log_context=context)


def log_err(context):
    context = str(context)
    if not context.endswith("\n"):
        context += "\n"
    GMLRuntime.Service.NKLogger.log(log_channel=LOG_CHANNEL,
                                    log_type=NKLogger.STD_ERR,
                                    log_context=context)


class GDC_SQLConnector(NKMySQLConnector):
    def __init__(self):
        super(GDC_SQLConnector, self).__init__(
            {
                'user': "GDC_Plugin",
                'password': "GDC_Passwd",
                'host': "10.10.20.2",
                'database': "GDataCenterV2",
            }
        )


class GDC(QThread):

    def __init__(self):
        super(GDC, self).__init__()

        # API Info and Settings (Fill in here)
        self.version = NKVersion("1.1.0")
        self.name = "GDC_V2"
        self.api_version = "1"  # Deprecated
        self.auto_start = True  # Deprecated
        self.minimal_GML_version = "1.6.2"  # Deprecated
        self.bc_expiration = 120

        # FLags for Main to Control (Check here repeatedly for flow control)
        self.stop_flag = False
        self.pause_flag = False

        # Status for GUI to access (Put value here for GUI to render)
        self.log_lines = []  # Deprecated
        self.log_progress_bar_precentage = 0  # Deprecated
        self.log_progress_bar_title = ""  # Deprecated
        self.log_progress_bar_color = 0  # Deprecated  0-Normal 1-Green 2-Red

        # Declare thread death here
        self.isDead = False

        # Private Storage
        self.sql_conn = GDC_SQLConnector()
        self.broadcast_channel_to_id_map = {}

        # Private Constants
        self.BC_CHANNEL_RESTART = 1
        self.BC_CHANNEL_SNAPSHOT = 2
        self.BC_CHANNEL_MESSAGE = 3
        self.BC_CHANNEL_EMERGENCY = 4
        self.BC_CHANNEL_CLOSE_MAYA = 5
        self.BC_MBOARD_ALL = "GOLD"

        # Tick Control
        self.tick = 0  # Current Tick
        self.MIN_TICK = 0  # Min interval is 0 tick
        self.MAX_TICK = 1000  # Max interval is 1000 tick
        self.ONE_TICK_DURATION = 0.1  # 1 tick = 0.1 seconds

    def run(self):
        # Minimal Requirement Precaution
        minimal_version = NKVersion("2.0.0")
        if GMLRuntime.App.version < minimal_version:
            log_err(f"Minimal Version GML V{minimal_version} is required.")
            self.stop_flag = True

        # Start-up Once
        if not self.stop_flag:
            log(self.str_hw_snapshot(GMLRuntime.Machine.hardware_snapshot))
            self.take_a_snapshot()
            self.init_broadcasts()

        while not self.stop_flag:
            if not self.pause_flag:
                # Frequency: 5s
                if self.tick % 50 == 0:
                    self.check_broadcasts()

                # Frequency: 30s
                if self.tick % 300 == 0:
                    self.update_online_status()

            time.sleep(self.ONE_TICK_DURATION)
            self.tick += 1
            if self.tick >= self.MAX_TICK:
                self.tick = self.MIN_TICK

        # MUST DECLARE DEATH IN THE END
        self.isDead = True

    def update_online_status(self):
        snapshot = GMLRuntime.Machine.hardware_snapshot
        my_mboard_id = snapshot["mboards"][0]["mboard_id"]

        sql_line = "INSERT INTO GDC_online_status " \
                   "(online_mboard_id, online_username, online_pc_name, online_ip, online_datetime) " \
                   "VALUES (%s, %s, %s, SUBSTRING_INDEX(USER(), '@', -1), %s) " \
                   "ON DUPLICATE KEY UPDATE " \
                   "online_username = VALUES(online_username), " \
                   "online_pc_name = VALUES(online_pc_name), " \
                   "online_ip = VALUES(online_ip), " \
                   "online_datetime = VALUES(online_datetime);"

        sql_data = (my_mboard_id, GMLRuntime.Machine.username, GMLRuntime.Machine.pc_name, datetime.now())
        try:
            result, errors = self.sql_conn.write(sql_line, sql_data)
            if errors:
                log_err("Update Online Status Failed:" + "".join(errors))
        except Exception as e:
            log_err("Update Online Status Failed: " + str(e))

    def init_broadcasts(self):
        try:
            latest_broadcasts, sql_errs = self.sql_conn.query("SELECT * FROM VIEW_broadcast_latest")
            if sql_errs:
                log_err("init_broadcasts SQL Errors\n" + sql_errs)
            for latest_broadcast in latest_broadcasts:
                self.broadcast_channel_to_id_map[latest_broadcast["bc_channel_id"]] = latest_broadcast["bc_id"]
            log("Init Broadcast Succeed.")
        except Exception as e:
            log_err("Init Broadcast Error: " + str(e))

    def check_broadcasts(self):
        # Check broadcasts
        try:
            latest_broadcasts, sql_errs = self.sql_conn.query("SELECT * FROM VIEW_broadcast_latest")
            if sql_errs:
                log_err("check_broadcasts SQL Errors\n" + sql_errs)
            for latest_broadcast in latest_broadcasts:
                broadcast_channel_latest_id = -1
                try:
                    broadcast_channel_latest_id = self.broadcast_channel_to_id_map[latest_broadcast["bc_channel_id"]]
                except:
                    self.broadcast_channel_to_id_map[latest_broadcast["bc_channel_id"]] = -1

                if broadcast_channel_latest_id != latest_broadcast["bc_id"]:
                    self.execute_broadcast(channel_id=latest_broadcast["bc_channel_id"],
                                           last_executed_bc_id=self.broadcast_channel_to_id_map[
                                               latest_broadcast["bc_channel_id"]
                                           ])
                    self.broadcast_channel_to_id_map[latest_broadcast["bc_channel_id"]] = latest_broadcast["bc_id"]
        except Exception as e:
            log_err("Check Broadcast Error\n" + traceback.format_exc())

    def is_active_bc(self, bc_datetime):
        now_datetime = datetime.now()

        if now_datetime < bc_datetime:
            return True
        elif (now_datetime - bc_datetime).seconds < self.bc_expiration:
            return True

        return False

    def execute_broadcast(self, channel_id, last_executed_bc_id):
        log("Execute Broadcast (Channel_ID: %i)" % (channel_id,))
        snapshot = GMLRuntime.Machine.hardware_snapshot
        my_mboard_id = snapshot["mboards"][0]["mboard_id"]

        if channel_id == self.BC_CHANNEL_RESTART:
            try:
                bc_detail, sql_errs = self.sql_conn.query(
                    "SELECT * FROM VIEW_broadcast_latest WHERE bc_channel_id = %i;" % channel_id)
                if sql_errs:
                    log_err("execute_broadcast SQL Errors\n" + sql_errs)
                bc_mboard_id = None
                try:
                    bc_mboard_id = bc_detail[0]["bc_mboard_id"]
                    bc_mboard_id = bc_mboard_id.decode()
                except:
                    pass
                if bc_mboard_id == my_mboard_id or bc_mboard_id == self.BC_MBOARD_ALL:
                    GMLRuntime.SatelliteApp.exit(restart=True)
                else:
                    log("MBoard_ID not match, broadcast ignored.")
            except Exception as e:
                log("Check Broadcast Detail Error: " + str(e))

        if channel_id == self.BC_CHANNEL_SNAPSHOT:
            try:
                bc_detail, sql_errs = self.sql_conn.query(
                    "SELECT * FROM VIEW_broadcast_latest WHERE bc_channel_id = %i;" % channel_id)
                if sql_errs:
                    log_err("BC_CHANNEL_SNAPSHOT SQL Errors\n" + sql_errs)
                bc_mboard_id = None
                try:
                    bc_mboard_id = bc_detail[0]["bc_mboard_id"]
                    bc_mboard_id = bc_mboard_id.decode()
                except:
                    pass
                if bc_mboard_id == my_mboard_id or bc_mboard_id == self.BC_MBOARD_ALL:
                    self.take_a_snapshot()
                else:
                    log("MBoard_ID not match, broadcast ignored.")
            except Exception as e:
                log("Check Broadcast Detail Error: " + str(e))

        if channel_id == self.BC_CHANNEL_MESSAGE:
            try:
                sql_line = "SELECT group_concat(bc_content SEPARATOR '\n\n') AS 'message' " \
                           "FROM GDC_broadcast " \
                           "WHERE " \
                           "(bc_mboard_id =%s OR bc_mboard_id = %s) " \
                           "AND " \
                           "bc_channel_id = %s " \
                           "AND " \
                           "bc_id > %s " \
                           "GROUP BY bc_channel_id;"
                sql_data = (my_mboard_id, self.BC_MBOARD_ALL, channel_id, last_executed_bc_id)
                bc_detail, sql_errs = self.sql_conn.query(sql_line, sql_data)
                if sql_errs:
                    log_err("BC_CHANNEL_MESSAGE SQL Errors\n" + sql_errs)
                log(bc_detail)

                try:
                    message = bc_detail[0]["message"]
                except Exception as e:
                    log("Get Message Failure: " + str(message))
                    message = ""

                if message:
                    GMLRuntime.Service.NKCmd.execute_command(f"alert {message}", None, None)
                    print("been here")

            except Exception as e:
                log("Check Broadcast Detail Error: " + str(e))

        # For safety issue, disable Emergency Broadcast

        # if channel_id == self.BC_CHANNEL_EMERGENCY:
        #     try:
        #         bc_detail = self.sql_conn.auto_query("SELECT * FROM VIEW_broadcast_latest WHERE bc_channel_id = %i;" %
        #                                              channel_id)
        #         bc_datetime = bc_detail[0]["bc_datetime"]
        #
        #         if self.is_active_bc(bc_datetime):
        #             log("EMERGENCY BROADCAST")
        #             GML_Globals.Core.launch_external_executable(
        #                 r"V:\TD\GMainLauncher\GML-1M\apps_for_all_project\GDualSystemSwitch\GDualSystemSwitch.exe")
        #         else:
        #             log("EXPIRED EMERGENCY BROADCAST")
        #     except Exception as e:
        #         log("EMERGENCY EXECUTION ERROR: " + str(e))

        # if channel_id == self.BC_CHANNEL_CLOSE_MAYA:
        #     try:
        #         bc_detail = self.sql_conn.auto_query("SELECT * FROM VIEW_broadcast_latest WHERE bc_channel_id = %i;" %
        #                                              channel_id)
        #         bc_mboard_id = None
        #         try:
        #             bc_mboard_id = bc_detail[0]["bc_mboard_id"]
        #             bc_mboard_id = bc_mboard_id.decode()
        #         except:
        #             pass
        #
        #         if bc_mboard_id == my_mboard_id or bc_mboard_id == self.BC_MBOARD_ALL:
        #             bc_datetime = bc_detail[0]["bc_datetime"]
        #
        #             if self.is_active_bc(bc_datetime):
        #                 log("CLOSE MAYA BROADCAST")
        #                 commands = ["taskkill /im maya.exe /f",
        #                             "taskkill /im AdAppMgrSvc.exe /f",
        #                             "taskkill /im AutodeskDesktopApp.exe /f",
        #                             "taskkill /im GenuineService.exe /f",
        #                             "taskkill /im LMU.exe /f"]
        #                 for command in commands:
        #                     try:
        #                         subprocess.check_output(command, shell=True)
        #                     except Exception as e:
        #                         log(str(e))
        #             else:
        #                 log("CLOSE MAYA:EXPIRED BROADCAST")
        #         else:
        #             log("CLOSE MAYA:MBoard_ID not match, broadcast ignored.")
        #
        #     except Exception as e:
        #         log("CLOSE MAYA: ERROR " + str(e))

    def take_a_snapshot(self):
        snapshot = GMLRuntime.Machine.hardware_snapshot

        # Insert cpu, mboard, hdrives to DB
        self.insert_hw_to_db(snapshot)

        # Insert GDC-Standard snapshot to DB
        self.insert_snapshot_to_db(snapshot)

        # Start Snapshot Difference Check
        self.initiate_snapshot_diff_procedure(snapshot)

    def str_hw_snapshot(self, snapshot):
        hwstr = ""

        for idx, hw in enumerate(snapshot["cpus"]):
            hwstr += "CPU%i:" % idx
            hwstr += "Name:%s, " % str(hw["cpu_name"])
            hwstr += "Serial:%s, " % str(hw["cpu_serial"])
            hwstr += "Cores:%i" % int(hw["cpu_core"])
        hwstr += "\n"

        for idx, hw in enumerate(snapshot["mboards"]):
            hwstr += "MBoard%i:" % idx
            hwstr += "Name:%s, " % str(hw["mboard_name"])
            hwstr += "Id:%s, " % str(hw["mboard_id"])
            hwstr += "Manufacturer:%s" % str(hw["mboard_mfr"])
        hwstr += "\n"

        for idx, hw in enumerate(snapshot["hdrives"]):
            hwstr += "HardDrive%i:" % idx
            hwstr += "Name:%s, " % str(hw["hdrive_name"])
            hwstr += "Id:%s, " % str(hw["hdrive_id"])
            hwstr += "Size:%i" % int(hw["hdrive_size_in_GB"])
        hwstr += "\n"

        hwstr += "VCard:%s\n" % str(snapshot["vcard"])
        hwstr += "Ram:%s\n" % str(snapshot["ram"])
        hwstr += "MAC:%s\n" % str(snapshot["mac"])

        return hwstr

    def insert_hw_to_db(self, snapshot):
        for hw in snapshot["cpus"]:
            create_sql_line = "INSERT IGNORE INTO GDC_hw_cpu " \
                              "(cpu_name, cpu_serial, cpu_core) " \
                              "VALUES (%s, %s, %s);"
            create_sql_data = (hw["cpu_name"],
                               hw["cpu_serial"],
                               hw["cpu_core"])

            try:
                result, errors = self.sql_conn.write(create_sql_line, create_sql_data)
                if errors:
                    log_err("CPU Insertion Failed:\n" + "".join(errors))
                else:
                    log("CPU Insertion Succeed.")
            except Exception as e:
                log_err("CPU Insertion Err: " + str(e))

        for hw in snapshot["mboards"]:
            create_sql_line = "INSERT IGNORE INTO GDC_hw_mboard " \
                              "(mboard_id, mboard_name, mboard_mfr) " \
                              "VALUES (%s, %s, %s);"
            create_sql_data = (hw["mboard_id"],
                               hw["mboard_name"],
                               hw["mboard_mfr"])
            try:
                result, errors = self.sql_conn.write(create_sql_line, create_sql_data)
                if errors:
                    log_err("MBoard Insertion Failed:\n" + "".join(errors))
                else:
                    log("MBoard Insertion Succeed.")
            except Exception as e:
                log_err("MBoard Insertion Err: " + str(e))

        for hw in snapshot["hdrives"]:
            create_sql_line = "INSERT IGNORE INTO GDC_hw_hdrive " \
                              "(hdrive_id, hdrive_name, hdrive_size_in_GB) " \
                              "VALUES (%s, %s, %s);"
            create_sql_data = (hw["hdrive_id"],
                               hw["hdrive_name"],
                               hw["hdrive_size_in_GB"])
            try:
                result, errors = self.sql_conn.write(create_sql_line, create_sql_data)
                if errors:
                    log_err("HDrive Insertion Failed:\n" + "".join(errors))
                else:
                    log("HDrive Insertion Succeed.")
            except Exception as e:
                log_err("HDrive Insertion Err: " + str(e))

    def insert_snapshot_to_db(self, snapshot):
        # SQL Transaction
        sql_lines = []

        # Main snapshot
        GDC_snapshot_line = "INSERT INTO GDC_snapshot (" \
                            "`snap_mboard_id`, " \
                            "`snap_ram`, " \
                            "`snap_vcard`, " \
                            "`snap_gml_ver`, " \
                            "`snap_username`, " \
                            "`snap_ad`, " \
                            "`snap_ip`, " \
                            "`snap_mac`, " \
                            "`snap_pc_name`, " \
                            "`snap_net_band`, " \
                            "`snap_tw_username`, " \
                            "`snap_tw_password`) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        try:
            net_bandwidth = psutil.net_if_stats()['\xd2\xd4\xcc\xab\xcd\xf8'].speed
        except:
            try:
                net_bandwidth = psutil.net_if_stats()[list(psutil.net_if_stats().keys())[0]].speed
            except:
                net_bandwidth = 0

        GDC_snapshot_data = (snapshot["mboards"][0]["mboard_id"],
                             snapshot["ram"],
                             snapshot["vcard"],
                             str(GMLRuntime.App.version),
                             GMLRuntime.Machine.username,
                             GMLRuntime.Machine.active_directory,
                             GMLRuntime.Machine.ip,
                             snapshot["mac"],
                             GMLRuntime.Machine.pc_name,
                             net_bandwidth,
                             "",
                             "")
        sql_lines.append([GDC_snapshot_line, GDC_snapshot_data])

        # CPU snapshot
        for hw in snapshot["cpus"]:
            sql_line = "INSERT INTO GDC_snapshot_cpu (" \
                       "`snap_id`, " \
                       "`cpu_name`) " \
                       "VALUES (last_insert_id(), %s);"
            sql_data = (hw["cpu_name"],)
            sql_lines.append([sql_line, sql_data])

        # HDRIVE snapshot
        for hw in snapshot["hdrives"]:
            sql_line = "INSERT INTO GDC_snapshot_hdrive (" \
                       "`snap_id`, " \
                       "`hdrive_id`) " \
                       "VALUES (last_insert_id(), %s);"
            sql_data = (hw["hdrive_id"],)
            sql_lines.append([sql_line, sql_data])

        # INSERTION
        try:
            result, errors = self.sql_conn.write_transaction(sql_lines)
            if errors:
                log_err("Snapshot Insertion Failed:\n" + "".join(errors))
            else:
                log("Snapshot Insertion Succeed.")
        except Exception as e:
            log_err("Snapshot Insertion Err: " + str(e))

    def initiate_snapshot_diff_procedure(self, snapshot):
        # VERIFICATION
        sql_line = "CALL PROC_snapdiff_check(%s);"
        sql_data = (snapshot["mboards"][0]["mboard_id"],)
        try:
            result, errors = self.sql_conn.write(sql_line, sql_data)
            if errors:
                log_err("Snapshot_Diff check Failed:\n" + "".join(errors))
            else:
                log("Snapshot_Diff check Succeed.")
        except Exception as e:
            log_err("Snapshot_Diff Err: " + str(e))

    def __str__(self):
        return "<GML_Plugin Instance [name:%s, version:%s, api_version:%s]>" % (
            self.name, self.version, self.api_version)
