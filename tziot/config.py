"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
配置文件
Authors: jdh99 <jdh821@163.com>
"""

import dcompy as dcom

TAG = 'tziot'

# 最大帧字节数
FRAME_MAX_LEN = 4096

PROTOCOL_NUM = 0

# 连接间隔.单位:s
CONN_INTERVAL = 30
# 连接超时时间.单位:s
CONN_TIMEOUT_MAX = 120

# 本机单播地址
local_ia = 0
local_pwd = ''

# 核心网参数
core_ia = 0x2141000000000002
core_ip = "115.28.86.171"
core_port = 12914
core_pipe = 0

# dcom参数
# dcom重发次数
dcom_retry_num = 5

# dcom重发间隔.单位:ms
dcom_retry_interval = 500


def init():
    global core_pipe
    core_pipe = dcom.addr_to_pipe(core_ip, core_port)


def config_core_param(ia: int, ip: str, port: int):
    """配置核心网参数"""
    global core_ia, core_ip, core_port, core_pipe
    core_ia = ia
    core_ip = ip
    core_port = port
    core_pipe = dcom.addr_to_pipe(ip, port)


def config_dcom_param(retry_num: int, retry_interval: int):
    """
    配置dcom参数
    :param retry_num: 重发次数
    :param retry_interval: 重发间隔.单位:ms
    """
    global dcom_retry_num, dcom_retry_interval

    if retry_num > 0:
        dcom_retry_num = retry_num
    if retry_interval > 0:
        dcom_retry_interval = retry_num
