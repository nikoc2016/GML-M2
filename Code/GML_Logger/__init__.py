import sys
import GML


class Logger:
    def __init__(self):

        external_log_file = None
        try:
            if GML.app_compiled:
                external_log_file = open(GML.app_log_path, "w")
        except:
            pass

        self.default_terminals = {
            "std_out": sys.stdout,
            "std_err": sys.stderr,
        }
        self.external_log_files = {
            "std_out": external_log_file,
            "std_err": external_log_file,
        }
        self.log_cache = ""
        self.logger_out = self.LogBuffer(self, "std_out")
        self.logger_err = self.LogBuffer(self, "std_err")

        sys.stdout = self.logger_out
        sys.stderr = self.logger_err

    class LogBuffer:
        def __init__(self, logger, std_type):
            self.logger = logger
            self.std_type = std_type

        def write(self, message):
            try:
                self.logger.default_terminals[self.std_type].write(message)
            except:
                pass

            try:
                self.logger.external_log_files[self.std_type].write(message)
            except:
                pass

            self.logger.log_cache += message

        def flush(self):
            try:
                self.logger.default_terminals[self.std_type].flush()
            except:
                pass

            try:
                self.logger.external_log_files[self.std_type].flush()
            except:
                pass
