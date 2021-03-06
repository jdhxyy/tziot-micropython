# 海萤物联网教程：MicroPython SDK
本文博客链接:[http://blog.csdn.net/jdh99](http://blog.csdn.net/jdh99),作者:jdh,转载请注明.

欢迎前往社区交流：[海萤物联网社区](http://www.ztziot.com)

[在线文档地址](https://jdhxyy.github.io/tziot)

## 简介
海萤物联网的MicroPython SDK是标准Python SDK移植到MicroPython的版本，标准版本可以查看文档：[海萤物联网教程：Python SDK](https://blog.csdn.net/jdh99/article/details/115415928)

MicroPython版本SDK在esp32中测试成功，esp8266资源太少不能运行。本文主要介绍MicroPython版本与标准版本的不同之处。

## 开源
- [github上的项目地址](https://github.com/jdhxyy/tziot-micropython)
- [gitee上的项目地址](https://gitee.com/jdhxyy/tziot-micropython)

## 安装
MicroPython版本的SDK已上传到pypi，包名是mciropython-tziot。此包依赖micropython-lagan，crcmodbus等若干个包。所以可以新建需求文件，然后一键全部下载。

新建文件requirements.txt，内容：
```text
micropython-tziot
micropython-lagan
micropython-dcompy
crcmodbus
knocky
sbc
utzpy
```

输入命令下载包到指定目录：
```text
pip install --target=d:/package -r requirements.txt
```

下载后文件如下图：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210405100333325.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2pkaDk5,size_16,color_FFFFFF,t_70)

删除掉egg-info等无关文件，将所有文件夹都上传到设备的lib目录下，即可在设备中使用。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210406050041511.png)


## API
MicroPython版本的SDK和标准版本的API接口全部一致，新增了两个函数：
```python
def connect_wifi(ssid: str, key=None, timeout=10) -> bool:
    """
    连接wifi
    :param ssid: wifi热点名
    :param key: wifi密码.不需要密码则填None
    :param timeout: 超时时间.单位:s
    :return: 返回True表示连接成功.False是连接失败
    """

def run(app):
    """运行应用程序.如果没有应用程序,app可填写None"""
```

### connect_wifi：连接wifi
esp32等可通过wifi联网的设备，可调用本函数连接wifi。

### run：运行用户应用程序
MicroPython在不同设备上函数嵌套深度各有不同，以esp32为例，主线程的嵌套深度为49，线程中只有10。所以将海萤物联网SDK部署在主线程，然后通过run函数开辟线程运行用户程序。所有用户代码需放在用户程序中。

## 示例
### 读取NTP时间
```python
import tziot
import time


pipe = 0


def main():
    global pipe
    
    print('connect wifi')
    ok = tziot.connect_wifi('JDHOME_MASTER', 'QWERASDFZXCV')
    if ok is False:
        print('connect wifi failed')
        return
    print('connect wlan success')
    
    pipe = tziot.bind_pipe_net(0x2141000000010029, pwd', '0.0.0.0', 12025)
    tziot.run(app)


def app():
    global pipe
    
    while not tziot.is_conn():
        time.sleep(0.1)
    resp, err = tziot.call(pipe, 0x2141000000000004, 1, 2000, bytearray())
    print("err:", err, "time:", resp)


if __name__ == '__main__':
    main()
```

输出：
```text
connect wifi
connect wlan success
err: 0 time: b'2021-04-06 05:23:00 +0800 CST'
```

### 对外提供灯控服务
开发板上有一个灯，通过GPIO2控制的。对外提供灯控服务，控制这个灯的亮灭。

服务号|服务
---|---
1|控制灯状态

- CON请求

字段|字节数
---|---
灯状态|1

- ACK应答：空

源码：
```python
import tziot
import time

from machine import Pin


# 服务号
RID_LED = 1

pipe = 0
gpio = None
state = False


def main():
    global pipe, gpio
    
    gpio = Pin(2, Pin.OUT)
    gpio.on()
    
    print('connect wifi')
    ok = tziot.connect_wifi('JDHOME_MASTER', 'QWERASDFZXCV')
    if ok is False:
        print('connect wifi failed')
        return
    print('connect wlan success')
    
    pipe = tziot.bind_pipe_net(0x2141000000010029, pwd, '0.0.0.0', 12025)
    tziot.register(RID_LED, ledService)
    tziot.run(None)
    

def ledService(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
    global state, gpio
    
    if len(req) != 1:
        return
    print('src ia:0x%x state:%d' % (src_ia, req[0]))
    
    if req[0]:
        gpio.on()
    else:
        gpio.off()
    
    return None, 0


if __name__ == '__main__':
    main()
```

用go语言编写一个测试程序控制灯灭然后3秒后亮：
```go
pipe, _ = tziot.BindPipeNet(0x2141000000000401, pwd, "192.168.1.119", 12021)
for tziot.IsConn() == false{}

resp, err := tziot.Call(pipe, 0x2141000000010029, 1, 3000, []uint8{0})
fmt.Println("err:", err, "time:", string(resp))
time.Sleep(3 * time.Second)
resp, err = tziot.Call(pipe, 0x2141000000010029, 1, 3000, []uint8{1})
fmt.Println("err:", err, "time:", string(resp))
```

设备LED会灭3秒然后亮，并有打印输出：
```text
connect wifi
connect wlan success
src ia:0x2141000000000401 state:0
src ia:0x2141000000000401 state:1
```
