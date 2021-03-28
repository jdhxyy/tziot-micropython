import tziot
import lagan
import time
import dcompy as dcom


def main():
    lagan.load()
    lagan.set_filter_level(lagan.LEVEL_DEBUG)
    lagan.enable_color(True)
    case1()


def case1():
    pipe = tziot.bind_pipe_net(0x2141000000000401, 'abc123', '192.168.1.119', 12025)
    while not tziot.is_conn():
        time.sleep(0.1)
    resp, err = tziot.call(pipe, 0x2141000000000004, 1, 1000, bytearray())
    print("err:", err, "time:", resp)


def case2():
    tziot.bind_pipe_net(0x2141000000000403, 'abc123', '192.168.1.119', 12025)
    while not tziot.is_conn():
        time.sleep(0.1)
    tziot.register(1, service1)


def service1(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
    print(dcom.pipe_to_addr(pipe), '0x%x' % src_ia, req)
    return bytearray(b'jdh99'), 0


if __name__ == '__main__':
    main()
