"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
管道操作
Authors: jdh99 <jdh821@163.com>
"""

import tziot.config as config
import tziot.param as param

import usocket
import _thread
import lagan
import dcompy as dcom
import utzpy as utz
import uasyncio as asyncio

PIPE_NET = 0xffff


class _Api:
    # 是否允许发送.函数原型:func() bool
    is_allow_send = None  # [[], bool]
    # 发送.函数原型:func(pipe: int, data: bytearray)
    send = None  # [[int, bytearray], None]


class _SocketRxItem:
    def __init__(self):
        self.is_rx = False
        self.pipe = 0
        self.data = bytearray()


_pipes = dict()
_pipe_num = 0
_socket = None
_observers = list()


_item = _SocketRxItem()


def init():
    loop = asyncio.get_event_loop()
    loop.create_task(_deal_socket_rx())


async def _deal_socket_rx():
    global _item
    while True:
        if _item.is_rx:
            pipe_receive(_item.pipe, _item.data)
            _item.is_rx = False
            continue
        await asyncio.sleep(0)


def pipe_bind_net(ia: int, pwd: str, ip: str, port: int) -> int:
    """ 绑定网络管道.绑定成功后返回管道号"""
    global _socket

    if _socket is not None:
        lagan.warn(config.TAG, "already bind pipe net")
        return PIPE_NET

    config.local_pwd = pwd
    _socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    _socket.bind((ip, port))
    _bind(PIPE_NET, ia, _socket_tx, _socket_is_allow_send)
    _thread.start_new_thread(_socket_rx, ())

    return PIPE_NET


def _socket_rx():
    global _socket, _item
    while True:
        data, address = _socket.recvfrom(config.FRAME_MAX_LEN)
        if len(data) == 0:
            continue
        lagan.info(config.TAG, 'udp rx:%r len:%d', address, len(data))
        lagan.print_hex(config.TAG, lagan.LEVEL_DEBUG, bytearray(data))

        if _item.is_rx:
            lagan.warn(config.TAG, 'udp rx:%r len:%d.deal is too slow!!!', address, len(data))
            continue
        _item.pipe = dcom.addr_to_pipe(address[0], address[1])
        _item.data = data
        _item.is_rx = True


def _socket_tx(pipe: int, data: bytearray):
    ip, port = dcom.pipe_to_addr(pipe)
    _socket.sendto(data, (ip, port))
    lagan.info(config.TAG, "udp send:ip:%s port:%d len:%d", ip, port, len(data))
    lagan.print_hex(config.TAG, lagan.LEVEL_DEBUG, data)


def _socket_is_allow_send() -> bool:
    return True


def pipe_receive(pipe: int, data: bytearray):
    """管道接收.pipe是发送方的管道号.如果是用户自己绑定管道,则在管道中接收到数据需回调本函数"""
    _notify_observers(pipe, data)


def _notify_observers(pipe: int, data: bytearray):
    global _observers

    for v in _observers:
        v(pipe, data)


def pipe_bind(ia: int, send, is_allow_send) -> int:
    """
    绑定管道.绑定成功后返回管道号
    :param ia: 设备单播地址
    :param send: 发送函数.格式:func(dst_pipe: int, data: bytearray)
    :param is_allow_send: 是否允许发送函数.格式:func() -> bool
    :return: 管道号
    """
    pipe = _get_pipe_num()
    _bind(pipe, ia, send, is_allow_send)
    return pipe


def _get_pipe_num() -> int:
    global _pipe_num

    _pipe_num += 1
    return _pipe_num


def _bind(pipe: int, ia: int, send, is_allow_send):
    config.local_ia = ia

    api = _Api()
    api.send = send
    api.is_allow_send = is_allow_send

    _pipes[pipe] = api


def pipe_is_allow_send(pipe: int) -> bool:
    if pipe >= PIPE_NET:
        pipe = PIPE_NET

    if pipe not in _pipes:
        return False
    return _pipes[pipe].is_allow_send()


def pipe_send(pipe: int, data: bytearray):
    if pipe == 0:
        return

    if pipe >= PIPE_NET:
        if PIPE_NET not in _pipes:
            return
        v = _pipes[PIPE_NET]
    else:
        if pipe not in _pipes:
            return
        v = _pipes[PIPE_NET]

    if pipe == PIPE_NET:
        if param.parent.ia == utz.IA_INVALID or not param.parent.is_conn:
            return
        v.send(param.parent.pipe, data)
    else:
        v.send(pipe, data)


def register_rx_observer(callback):
    """
    注册接收观察者
    :param callback: 回调函数格式:func(pipe: int, data: bytearray)
    """
    _observers.append(callback)
