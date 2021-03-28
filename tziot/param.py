"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
公共参数
Authors: jdh99 <jdh821@163.com>
"""


class ParentInfo:
    """父路由信息"""

    def __init__(self):
        self.ia = 0
        self.pipe = 0
        self.cost = 0
        self.is_conn = False
        self.timestamp = 0


parent = ParentInfo()
