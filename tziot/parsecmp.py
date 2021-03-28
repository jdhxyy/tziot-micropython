"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
CMP协议解析处理
Authors: jdh99 <jdh821@163.com>
"""

import tziot.standardlayer as standardlayer
import tziot.config as config

import knocky as knock
import utzpy as utz
import lagan


def init():
    standardlayer.register_rx_observer(_deal_rx)


def _deal_rx(data: bytearray, standard_header: utz.StandardHeader, pipe: int):
    if standard_header.dst_ia != config.local_ia or standard_header.next_head != utz.HEADER_CMP:
        return

    payload = utz.flp_frame_to_bytes(data)
    if payload is None:
        lagan.warn(config.TAG, "parse cmp failed.flp frame to bytes failed")
        return

    if len(payload) == 0:
        lagan.warn(config.TAG, "parse cmp failed.payload len is wrong:%d", len(payload))
        return

    knock.call(utz.HEADER_CMP, payload[0], payload[1:])
