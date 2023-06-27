import json
import os

import yaml

from NikoKit.NikoLib import NKFileSystem
from NikoKit.NikoStd import NKLaunch
import os.path as p

HELP_TEXT = """
LaunchPad 启动项简介


*层级结构
Config
    LaunchPad
        boot
            boot.json
            boot_maya.json
            boot_maya_2022.json
            boot_deadline_slave.json
            boot_deadline_monitor.json
            
        plan
            plan.yaml
            plan_maya_suite.yaml
            plan_deadline_suite.yaml

        proj
            proj.yaml
            proj_a.yaml
            proj_b.yaml


*名词解释
boot:    单个APP启动项, 必须以boot_开头, JSON格式
plan:    多个APP启动项(套装), 必须以plan_开头, YAML格式
project: 项目的启动项，内容包含boot和plan, YAML格式


*继承
1. 名字包含代表继承: boot.json <- boot_maya.json <- boot_maya_2022.json
2. 名字相似并不会继承: plan_houdini_1.yaml <---X--- plan_houdini_2.yaml

*配置格式详解 【复制example文件并编辑最为安全】

1.boot
四种启动方式介绍
run                    -最全能的启动方式，可以隐藏窗口，传递环境变量，启动路径
run_system             -兼容性启动，以操作系统来运行命令，只能运行一行命令，有黑框
run_system_sequential  -兼容性启动，以操作系统来运行命令，能有序运行多行命令，有黑框
gml_cmd                -GML内部执行对应命令行，注意是GML命令

======================= 启动方式:run ==============+============
{
  "app_category": "Demo",                              # APP类别
  "app_display_name": "BOOT_RUN",                      # APP名称
  "app_icon": "demo.png",                              # APP图标
  "app_tooltip": "This is an example for method run",  # APP简介
  "app_run": {                                         # APP启动Dict
    "method": "run",                                   # 启动方法
    "params": {                                        # 启动参数
      "command": [                                     # 命令行
        "cmd.exe",
        "/k",
        "@echo off && echo %env_1% %env_2%"
      ],
      "custom_env": {                                  # 环境变量
        "env_1": "hello",
        "env_2": "world"
      },
      "cwd": null,                                     # 起始路径
      "display_mode": "SW_SHOWNORMAL"                  # "SW_HIDE", "SW_SHOWNORMAL", "SW_MINIMIZE", "SW_MAXIMIZE"
    }
  }
}
=====================================================================

======================= 启动方式:run_system ==============+============
{
  "app_category": "Demo",                                     # APP类别
  "app_display_name": "BOOT_RUN_SYSTEM",                      # APP名称
  "app_icon": "demo.png",                                     # APP图标
  "app_tooltip": "This is an example for method run_system",  # APP简介
  "app_run": {                                                # APP启动Dict 
    "method": "run_system",                                   # 启动方法
    "params": {                                               # 启动参数
      "command": [                                            # 命令行
        "cmd.exe",
        "/k",
        "echo hello world"
      ],
      "pause": false                                          # 运行后暂停cmd.exe
    }
  }
}
=====================================================================

================== 启动方式:run_system_sequential ====================
{
  "app_category": "Demo",                                                # APP类别
  "app_display_name": "BOOT_RUN_SYSTEM_SEQUENTIAL",                      # APP名称
  "app_icon": "demo.png",                                                # APP图标
  "app_tooltip": "This is an example for method run_system_sequential",  # APP简介
  "app_run": {                                                           # APP启动Dict 
    "method": "run_system_sequential",                                   # 启动方法
    "params": {                                                          # 启动参数
      "command": [
        [                                                                # 命令行#1
          "ping",
          "-n",
          "3",
          "127.0.0.1"
        ],
        [                                                                # 命令行#2
          "start",
          "calc.exe"
        ]
      ],
      "pause": true                                                      # 运行后暂停cmd.exe
    }
  }
}
=====================================================================

======================= 启动方式:gml_cmd ==============+============
{
  "app_category": "Demo",                                     # APP类别
  "app_display_name": "BOOT_GML_CMD",                         # APP名称
  "app_icon": "demo.png",                                     # APP图标
  "app_tooltip": "This is an example for method gml_cmd",     # APP简介
  "app_run": {                                                # APP启动Dict 
    "method": "gml_cmd",                                      # 启动方法
    "params": {                                               # 启动参数
      "command": "awake LaunchPad"                            # GML命令行
    }
  }
}
=====================================================================



2.plan
====================== plan_deadline_suite.yaml ==========================
- deadline_slave                        boot.yaml的文件名
- deadline_monitor                      boot.yaml的文件名
=====================================================================




3.projects
========================= my_project.yaml ==========================
- boot_maya_2022                        boot
- plan_deadline_suite                   plan
- deadline_monitor                      boot
=====================================================================)
"""


def spawn_launch_pad_config_dir():
    NKFileSystem.delete_try(r"../../../config/LaunchPad")
    NKFileSystem.scout(r"../../../config/LaunchPad\boot")
    NKFileSystem.scout(r"../../../config/LaunchPad\proj")
    NKFileSystem.scout(r"../../../config/LaunchPad\plan")
    with open(r"../../../config/LaunchPad\Readme.txt", "w") as f:
        f.write(HELP_TEXT)

    boot_gml_it_ticket = {
        'app_category': "通用工具",
        'app_display_name': "提交IT工单",
        'app_icon': "demo.png",
        'app_tooltip': "使用此工具提交IT工单",
        'app_run': {
            'method': 'gml_cmd',
            'params': {
                r'command': "ticket"
            },
        }
    }

    boot_ex_run = {
        'app_category': "Demo",
        'app_display_name': "BOOT_RUN",
        'app_icon': "demo.png",
        'app_tooltip': "This is an example for method run",
        'app_run': {
            'method': 'run',
            'params': {
                r'command': ["cmd.exe", "/k", "@echo off && echo %env_1% %env_2%"],
                r'custom_env': {"env_1": "hello", "env_2": "world"},
                r'cwd': None,
                r'display_mode': "SW_SHOWNORMAL",
            },
        },
    }

    boot_ex_run_system = {
        'app_category': "Demo",
        'app_display_name': "BOOT_RUN_SYSTEM",
        'app_icon': "demo.png",
        'app_tooltip': "This is an example for method run_system",
        'app_run': {
            'method': 'run_system',
            'params': {
                r'command': ["cmd.exe", "/k", "echo hello world"],
                r'pause': False
            },
        },
    }

    boot_ex_run_system_sequential = {
        'app_category': "Demo",
        'app_display_name': "BOOT_RUN_SYSTEM_SEQUENTIAL",
        'app_icon': "demo.png",
        'app_tooltip': "This is an example for method run_system_sequential",
        'app_run': {
            'method': 'run_system_sequential',
            'params': {
                r'command': [["ping", "-n", "3", "127.0.0.1"],
                             ["start", "calc.exe"]],
                r'pause': True
            },
        },
    }

    boot_ex_gml_cmd = {
        'app_category': "Demo",
        'app_display_name': "BOOT_GML_CMD",
        'app_icon': "demo.png",
        'app_tooltip': "This is an example for method gml_cmd",
        'app_run': {
            'method': 'gml_cmd',
            'params': {
                r'command': "awake LaunchPad"
            },
        }
    }

    plan_ex_run_suite = ["boot_ex_run", "boot_ex_run_system", "boot_ex_run_system_sequential"]

    project_ex = ["boot_ex_gml_cmd", "plan_ex_run_suite"]

    boot = {
        "app_category": "Standard",
        "app_display_name": "GML Application",
        "app_icon": "demo.png",
        "app_tooltip": "An GML Application",
        "app_run": {
            "method": None,
            "params": None
        }
    }

    plan = []

    plan_general = ["boot_gml_it_ticket"]

    proj = ["plan_general"]

    with open(r"../../../config/LaunchPad\boot\boot_gml_it_ticket.json", "w") as f:
        json.dump(boot_gml_it_ticket, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad\boot\boot_ex_run.json", "w") as f:
        json.dump(boot_ex_run, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad\boot\boot_ex_run_system.json", "w") as f:
        json.dump(boot_ex_run_system, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad\boot\boot_ex_run_system_sequential.json", "w") as f:
        json.dump(boot_ex_run_system_sequential, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad\boot\boot_ex_gml_cmd.json", "w") as f:
        json.dump(boot_ex_gml_cmd, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad/plan/plan_ex_run_suite.yaml", "w") as f:
        yaml.dump(plan_ex_run_suite, f)

    with open(r"../../../config/LaunchPad/plan/plan_general.yaml", "w") as f:
        yaml.dump(plan_general, f)

    with open(r"../../../config/LaunchPad\proj\proj_ex.yaml", "w") as f:
        yaml.dump(project_ex, f)

    with open(r"../../../config/LaunchPad\boot\boot.json", "w") as f:
        json.dump(boot, f, ensure_ascii=False, indent=2)

    with open(r"../../../config/LaunchPad\plan\plan.yaml", "w") as f:
        yaml.dump(plan, f)

    with open(r"../../../config/LaunchPad\proj\proj.yaml", "w") as f:
        yaml.dump(proj, f)


def convert_v_boots():
    boot_folder = r"V:\TD\GMainLauncher\GML-1M\boot_manager\boot_config"
    proj_folder = r"V:\TD\GMainLauncher\GML-1M\boot_manager\project_config"

    boot_name_to_obj = {}
    proj_name_to_obj = {}

    for boot_file in os.listdir(boot_folder):
        with open(p.join(boot_folder, boot_file), "r", encoding="utf-8") as f:
            boot_name_to_obj[p.splitext(boot_file)[0]] = yaml.load(f, Loader=yaml.FullLoader)

    for proj_file in os.listdir(proj_folder):
        with open(p.join(proj_folder, proj_file), "r", encoding="utf") as f:
            proj_name_to_obj[p.splitext(proj_file)[0]] = yaml.load(f, Loader=yaml.FullLoader)

    for boot_name, boot_obj in boot_name_to_obj.items():
        target_obj = {}
        try:
            target_obj["app_category"] = boot_obj["app_category"]
        except:
            pass

        try:
            target_obj["app_display_name"] = boot_obj["app_name"]
        except:
            pass

        try:
            target_obj["app_icon"] = boot_obj["app_icon"]
        except:
            pass

        try:
            target_obj["app_tooltip"] = boot_obj["app_short_description"]
        except:
            pass

        target_obj["app_run"] = {
            "method": "run_system",
            "params": {
                "command": boot_obj["app_launch_path"],
                "pause": False,
            }
        }
        with open(fr"../../../config/LaunchPad\boot\boot_{boot_name}.json", "w", encoding="gbk") as f:
            json.dump(target_obj, f, ensure_ascii=False, indent=2)

    for proj_name, proj_obj in proj_name_to_obj.items():
        target_obj = [f"boot_{boot_name}" for boot_name in proj_obj]
        with open(fr"../../../config/LaunchPad\proj\proj_{proj_name}.yaml", "w", encoding="gbk") as f:
            yaml.dump(target_obj, f)


spawn_launch_pad_config_dir()
convert_v_boots()
