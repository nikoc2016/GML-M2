
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
