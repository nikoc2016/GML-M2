
LaunchPad ��������


*�㼶�ṹ
Config
    WorkforceMonitor
        org
            org.yaml

        proj
            proj.yaml


*���ʽ���
org:    ���APP������(��װ), ������plan_��ͷ, YAML��ʽ
proj:   ��Ŀ����������ݰ���boot��plan, YAML��ʽ


*�̳�
1. ���ְ�������̳�: boot.json <- boot_maya.json <- boot_maya_2022.json
2. �������Ʋ�����̳�: plan_houdini_1.yaml <---X--- plan_houdini_2.yaml

*���ø�ʽ��� ������example�ļ����༭��Ϊ��ȫ��

1.organization
====================== plan_deadline_suite.yaml ==========================
- deadline_slave                        boot.yaml���ļ���
- deadline_monitor                      boot.yaml���ļ���
=====================================================================


2.projects
========================= my_project.yaml ==========================
- boot_maya_2022                        boot
- plan_deadline_suite                   plan
- deadline_monitor                      boot
=====================================================================
