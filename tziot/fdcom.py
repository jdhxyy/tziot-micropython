"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
dcom操作
Authors: jdh99 <jdh821@163.com>
"""

import tziot.config as config
import tziot.fpipe as fpipe
import tziot.standardlayer as standardlayer

import dcompy as dcom
import lagan
import utzpy as utz

# dcom是否初始化
is_dcom_init = False


def init_dcom():
    """初始化dcom.全局只应该初始化一次"""
    global is_dcom_init

    if is_dcom_init:
        return

    param = dcom.LoadParam()
    param.block_retry_max_num = config.dcom_retry_num
    param.block_retry_interval = config.dcom_retry_interval
    param.is_allow_send = fpipe.pipe_is_allow_send
    param.send = _dcom_send
    dcom.load(param)

    standardlayer.register_rx_observer(_deal_rx)
    is_dcom_init = True


def _dcom_send(protocol: int, pipe: int, dst_ia: int, data: bytearray):
    flp_frame = utz.bytes_to_flp_frame(data, True, 0)

    header = utz.StandardHeader()
    header.version = utz.PROTOCOL_VERSION
    header.frame_index = utz.generate_frame_index()
    header.payload_len = len(flp_frame)
    header.next_head = utz.HEADER_FLP
    header.hops_limit = 0xff
    header.src_ia = config.local_ia
    header.dst_ia = dst_ia

    standardlayer.send(flp_frame, header, pipe)


def _deal_rx(data: bytearray, standard_header: utz.StandardHeader, pipe: int):
    """处理标准层回调函数"""
    if standard_header.dst_ia != config.local_ia or standard_header.next_head != utz.HEADER_FLP:
        return

    body = utz.flp_frame_to_bytes(data)
    if body is None:
        lagan.warn(config.TAG, "flp frame to bytes failed!src ia:0x%x", standard_header.src_ia)
        return
    dcom.receive(config.PROTOCOL_NUM, pipe, standard_header.src_ia, body)
