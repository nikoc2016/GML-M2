import os.path as p
from NikoKit.NikoLib import NKFileSystem
from NikoKit.NikoLib.NKFileSystem import get_exe_info
from NikoKit.NikoLib.NKResource import NKResource
from NikoKit.NikoStd import NKLaunch

NIKO_KIT_DIR = r"D:\gtec_media_dev\Lib\Python\General\NikoKit"
PYLIB_DIR = r"C:\Python39\Lib\site-packages"
SERVER_ADDR = "10.10.20.4"


class Runtime:
    compiled = None
    my_dir = None
    my_file_name = None
    my_file_ext = None


def main():
    Runtime.compiled, Runtime.my_dir, Runtime.my_file_name, Runtime.my_file_ext = get_exe_info(__file__)

    features = [
        ("Pip Install Req", pip_install_req),
        ("Pack Res", pack_resource),
        ("(Unnecessary) Clear Compiled", clear_compiled),
        ("Clean Icon Cache", clear_icon_cache),
        ("Compile GMLG", compile_gml_g),
        ("Compile GML", compile_gml),
        ("Compile GML-No-Console", compile_gml_no_console),
        ("Prepare ServerSpace->Distribute", copy_libs_to_dist),
        ("Server write mode", server_write_mode),
        ("Server read mode", server_read_mode)
    ]

    while True:
        print("0. Exit")
        for idx, feature in enumerate(features):
            print(f"{idx + 1}. {feature[0]}")
        choice = int(input("Number:"))
        if choice == 0:
            return
        else:
            features[choice - 1][1]()


def pip_install_req():
    NKLaunch.run_system(["pip3", "install", "-r", p.join(Runtime.my_dir, "requirements.txt")], pause=True)


def pack_resource():
    NKResource.pack_dir_to_res(res_dir=p.join(Runtime.my_dir, "Res"),
                               res_lib_path=p.join(Runtime.my_dir, "Client", "GML", "Res.py"),
                               ext_list=[".png"])


def clear_compiled():
    NKFileSystem.delete_try(p.join(Runtime.my_dir, "Distribute", "GML"))


def compile_gml_g():
    commands = [["robocopy", "/MIR", NIKO_KIT_DIR, p.join(Runtime.my_dir, "Client", "GMLG", "NikoKit")],
                ["PyInstaller", "-Fa", p.join(Runtime.my_dir, "Client", "GMLG", "GMLG.py"),
                 "-i", p.join(Runtime.my_dir, "res", "GMLG.ico"),
                 "--clean",
                 "--distpath", p.join(Runtime.my_dir, "Distribute", "GML")
                 ],
                ["rd", "/s", "/q", p.join(Runtime.my_dir, "Client", "GMLG", "NikoKit")]]

    NKLaunch.run_system_sequential(commands, pause=True)


def compile_gml():
    NKLaunch.run_system(command=["PyInstaller", "-Fa", p.join(Runtime.my_dir, "Client", "GML", "GML.py"),
                                 "-i", p.join(Runtime.my_dir, "res", "GML.ico"),
                                 "--clean",
                                 "--distpath", p.join(Runtime.my_dir, "Distribute", "GML")], pause=True)


def compile_gml_no_console():
    NKLaunch.run_system(command=["PyInstaller", "-Fa", p.join(Runtime.my_dir, "Client", "GML", "GML.py"),
                                 "-i", p.join(Runtime.my_dir, "res", "GML.ico"),
                                 "--clean",
                                 "--distpath", p.join(Runtime.my_dir, "Distribute", "GML"),
                                 "-w"], pause=True)


def copy_libs_to_dist():
    copy_server_space = ['robocopy', '/MIR',
                         p.join(Runtime.my_dir, "Client", "GML", "ServerSpace"),
                         p.join(Runtime.my_dir, "Distribute", "GML", "ServerSpace")]
    copy_shiboken2 = ['robocopy', '/MIR',
                      p.join(PYLIB_DIR, "shiboken2"),
                      p.join(Runtime.my_dir, "Distribute", "GML", "ServerSpace", "gml", "lib", "shiboken2")]
    copy_pyside2 = ['robocopy', '/MIR',
                    p.join(PYLIB_DIR, "PySide2"),
                    p.join(Runtime.my_dir, "Distribute", "GML", "ServerSpace", "gml", "lib", "PySide2")]
    copy_niko_kit = ['robocopy', '/MIR',
                     p.join(NIKO_KIT_DIR),
                     p.join(Runtime.my_dir, "Distribute", "GML", "ServerSpace", "gml", "lib", "NikoKit")]

    NKLaunch.run_system_sequential([copy_server_space, copy_shiboken2, copy_pyside2, copy_niko_kit])


def clear_icon_cache():
    commands = ['taskkill /f /im explorer.exe',
                'attrib -h -s -r "%userprofile%AppDataLocalIconCache.db"',
                'del /f "%userprofile%AppDataLocalIconCache.db"',
                'attrib /s /d -h -s -r "%userprofile%AppDataLocalMicrosoftWindowsExplorer*"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_32.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_96.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_102.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_256.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_1024.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_idx.db"',
                'del /f "%userprofile%AppDataLocalMicrosoftWindowsExplorer	humbcache_sr.db"',
                'echo y|reg delete "HKEY_CLASSES_ROOTLocal SettingsSoftwareMicrosoftWindowsCurrentVersionTrayNotify" /v IconStreams',
                'echo y|reg delete "HKEY_CLASSES_ROOTLocal SettingsSoftwareMicrosoftWindowsCurrentVersionTrayNotify" /v PastIconsStream',
                'start explorer']
    NKLaunch.run_system_sequential(commands)


def server_write_mode():
    commands = [
        fr'net use \\{SERVER_ADDR} /del',
        fr'net use \\{SERVER_ADDR} /user:super super',
        fr'start \\{SERVER_ADDR}'
    ]
    NKLaunch.run_system_sequential(commands)


def server_read_mode():
    commands = [
        fr'net use \\{SERVER_ADDR} /del',
        fr'net use \\{SERVER_ADDR} /user:normal normal',
        fr'start \\{SERVER_ADDR}'
    ]
    NKLaunch.run_system_sequential(commands)


if __name__ == "__main__":
    main()
