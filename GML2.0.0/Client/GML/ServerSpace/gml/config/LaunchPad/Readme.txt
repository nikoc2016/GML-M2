
LaunchPad ��������


*�㼶�ṹ
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


*���ʽ���
boot:    ����APP������, ������boot_��ͷ, JSON��ʽ
plan:    ���APP������(��װ), ������plan_��ͷ, YAML��ʽ
project: ��Ŀ����������ݰ���boot��plan, YAML��ʽ


*�̳�
1. ���ְ�������̳�: boot.json <- boot_maya.json <- boot_maya_2022.json
2. �������Ʋ�����̳�: plan_houdini_1.yaml <---X--- plan_houdini_2.yaml

*���ø�ʽ��� ������example�ļ����༭��Ϊ��ȫ��

1.boot
����������ʽ����
run                    -��ȫ�ܵ�������ʽ���������ش��ڣ����ݻ�������������·��
run_system             -�������������Բ���ϵͳ���������ֻ������һ������кڿ�
run_system_sequential  -�������������Բ���ϵͳ������������������ж�������кڿ�
gml_cmd                -GML�ڲ�ִ�ж�Ӧ�����У�ע����GML����

======================= ������ʽ:run ==============+============
{
  "app_category": "Demo",                              # APP���
  "app_display_name": "BOOT_RUN",                      # APP����
  "app_icon": "demo.png",                              # APPͼ��
  "app_tooltip": "This is an example for method run",  # APP���
  "app_run": {                                         # APP����Dict
    "method": "run",                                   # ��������
    "params": {                                        # ��������
      "command": [                                     # ������
        "cmd.exe",
        "/k",
        "@echo off && echo %env_1% %env_2%"
      ],
      "custom_env": {                                  # ��������
        "env_1": "hello",
        "env_2": "world"
      },
      "cwd": null,                                     # ��ʼ·��
      "display_mode": "SW_SHOWNORMAL"                  # "SW_HIDE", "SW_SHOWNORMAL", "SW_MINIMIZE", "SW_MAXIMIZE"
    }
  }
}
=====================================================================

======================= ������ʽ:run_system ==============+============
{
  "app_category": "Demo",                                     # APP���
  "app_display_name": "BOOT_RUN_SYSTEM",                      # APP����
  "app_icon": "demo.png",                                     # APPͼ��
  "app_tooltip": "This is an example for method run_system",  # APP���
  "app_run": {                                                # APP����Dict 
    "method": "run_system",                                   # ��������
    "params": {                                               # ��������
      "command": [                                            # ������
        "cmd.exe",
        "/k",
        "echo hello world"
      ],
      "pause": false                                          # ���к���ͣcmd.exe
    }
  }
}
=====================================================================

================== ������ʽ:run_system_sequential ====================
{
  "app_category": "Demo",                                                # APP���
  "app_display_name": "BOOT_RUN_SYSTEM_SEQUENTIAL",                      # APP����
  "app_icon": "demo.png",                                                # APPͼ��
  "app_tooltip": "This is an example for method run_system_sequential",  # APP���
  "app_run": {                                                           # APP����Dict 
    "method": "run_system_sequential",                                   # ��������
    "params": {                                                          # ��������
      "command": [
        [                                                                # ������#1
          "ping",
          "-n",
          "3",
          "127.0.0.1"
        ],
        [                                                                # ������#2
          "start",
          "calc.exe"
        ]
      ],
      "pause": true                                                      # ���к���ͣcmd.exe
    }
  }
}
=====================================================================

======================= ������ʽ:gml_cmd ==============+============
{
  "app_category": "Demo",                                     # APP���
  "app_display_name": "BOOT_GML_CMD",                         # APP����
  "app_icon": "demo.png",                                     # APPͼ��
  "app_tooltip": "This is an example for method gml_cmd",     # APP���
  "app_run": {                                                # APP����Dict 
    "method": "gml_cmd",                                      # ��������
    "params": {                                               # ��������
      "command": "awake LaunchPad"                            # GML������
    }
  }
}
=====================================================================



2.plan
====================== plan_deadline_suite.yaml ==========================
- deadline_slave                        boot.yaml���ļ���
- deadline_monitor                      boot.yaml���ļ���
=====================================================================




3.projects
========================= my_project.yaml ==========================
- boot_maya_2022                        boot
- plan_deadline_suite                   plan
- deadline_monitor                      boot
=====================================================================)
