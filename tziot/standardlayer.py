"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
标准层处理模块
Authors: jdh99 <jdh821@163.com>
"""

import tziot.config as config
import tziot.fpipe as fpipe

import lagan
import utzpy as utz

_observers = list()


def init():
    fpipe.register_rx_observer(_rx)


def _rx(pipe: int, data: bytearray):
    """标准层接收"""
    header = _get_standard_header(data)
    if header is None:
        return

    _notify_observers(data[utz.NLV1_HEAD_LEN:], header, pipe)


def _get_standard_header(data: bytearray):
    header, offset = utz.bytes_to_standard_header(data)  # type: utz.StandardHeader, int
    if header is None or offset == 0:
        lagan.debug(config.TAG, 'get standard header failed:bytes to standard header failed')
        return None

    if header.version != utz.PROTOCOL_VERSION:
        lagan.debug(config.TAG, "get standard header failed:protocol version is not match:%d", header.version)
        return None

    if header.payload_len + offset != len(data):
        lagan.debug(config.TAG, "get standard header failed:payload len is not match:%d", header.payload_len)
        return None
    return header


def _notify_observers(data: bytearray, standard_header: utz.StandardHeader, pipe: int):
    global _observers

    for v in _observers:
        v(data, standard_header, pipe)


def register_rx_observer(callback):
    """
    注册接收观察者
    :param callback: 回调函数格式:func(data: bytearray, standardHeader: utz.StandardHeader, pipe: int)
    """
    _observers.append(callback)


def send(data: bytearray, standard_header: utz.StandardHeader, pipe: int):
    """基于标准头部发送"""
    data_len = len(data)
    if data_len > config.FRAME_MAX_LEN:
        lagan.error(config.TAG, "standard layer send failed!data len is too long:%d src ia:0x%x dst ia:0x%x", data_len,
                    standard_header.src_ia, standard_header.dst_ia)
        return

    if standard_header.payload_len != data_len:
        standard_header.payload_len = data_len

    frame = utz.standard_header_to_bytes(standard_header)
    frame += data
    fpipe.pipe_send(pipe, frame)
