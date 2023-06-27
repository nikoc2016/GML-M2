import os
import subprocess
import win32con


class LaunchExternal:
    DISPLAY_MODE_HIDE = win32con.SW_HIDE
    DISPLAY_MODE_NORMAL = win32con.SW_SHOWNORMAL
    DISPLAY_MODE_MINIMIZED = win32con.SW_MINIMIZE
    DISPLAY_MODE_MAXIMIZE = win32con.SW_MAXIMIZE

    @staticmethod
    def run(command,
            cwd=None,
            display_mode=DISPLAY_MODE_HIDE,
            custom_env=None):
        """

        Args:
            command: Command or EXE path and Args
            cwd: EXE starting directory
            display_mode: Decides how the window is shown
            0 - SW_HIDE
            1 - SW_SHOWNORMAL | SW_NORMAL
            2 - SW_SHOWMINIMIZED
            3 - SW_MAXIMIZE
            custom_env:  Dict overrides sys.environ   ex. {"MAYA_PATH": "C:/Maya"}

        Returns:
                subprocess.Popen()
        """
        si = subprocess.STARTUPINFO()
        si.dwFlags = win32con.STARTF_USESHOWWINDOW
        si.wShowWindow = display_mode

        return subprocess.Popen(command,
                                startupinfo=si,
                                creationflags=subprocess.CREATE_NEW_CONSOLE,
                                env={**os.environ, **custom_env},
                                cwd=cwd
                                )

    @staticmethod
    def run_pipe(command,
                 cwd=None,
                 custom_env=None):
        """

        Args:
            command: Command or EXE path and Args
            cwd: EXE starting directory
            custom_env:  Dict overrides sys.environ   ex. {"MAYA_PATH": "C:/Maya"}

        Returns:
                subprocess.Popen()
        """
        return subprocess.Popen(command,
                                creationflags=subprocess.CREATE_NO_WINDOW,
                                env={**os.environ, **custom_env},
                                cwd=cwd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )

    @staticmethod
    def example_pipe_handling(process):
        """
        This is a example of how to deal with piping result in real-time

        Args:
            process: subprocess.Process

        Returns:

        """
        while process.poll() is None:
            new_line = process.stdout.readline().decode()
            if new_line == "Done":
                continue
            else:
                number = int(new_line)
                print("Progress: " + str(number))
                print("Result: " + str(number + number))
