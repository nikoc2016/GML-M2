
LaunchPad 启动项简介


*层级结构
Config
    WorkforceMonitor
        org
            org.yaml

        proj
            proj.yaml


*名词解释
org:    多个APP启动项(套装), 必须以plan_开头, YAML格式
proj:   项目的启动项，内容包含boot和plan, YAML格式


*继承
1. 名字包含代表继承: boot.json <- boot_maya.json <- boot_maya_2022.json
2. 名字相似并不会继承: plan_houdini_1.yaml <---X--- plan_houdini_2.yaml

*配置格式详解 【复制example文件并编辑最为安全】

1.organization
====================== plan_deadline_suite.yaml ==========================
- deadline_slave                        boot.yaml的文件名
- deadline_monitor                      boot.yaml的文件名
=====================================================================


2.projects
========================= my_project.yaml ==========================
- boot_maya_2022                        boot
- plan_deadline_suite                   plan
- deadline_monitor                      boot
=====================================================================
