# lib-pahao-mqtt
基于paho.mqtt.client封装的辅助类，隐藏了一些不常用业务场景下的方法和特性。

# How to install paho.mqtt

pip install paho-mqtt

# What Required

* Python 3.5+
* paho-mqtt 1.4
* Python3 venv

# How it works

定义 on_connect() 回调函数

```  define on_connect()

def on_connect(client, userdata, flags, rc):
    if "0" == str(rc):
        topic = input("Connect success....plz input topic that you wish to listen:")
        if len(topic) > 0:
            client.subscribe(topic)
            print("listen starting...")
        else:
            print("Connected.")
```

定义 on_message() 回调函数 

```
def on_message(client, userdata, message):
    print("Received message:",message.payload.decode("utf-8"))
    client.publish("test/reply","这是一句回复")
```

声明 MqttAssist 实例
```
client = MqttAssist()
```
绑定回调函数 

```
client.event("on_connect",on_connect)
client.event("on_message",on_message)
```
调用connect()与代理进行连接
```
host = { "host":"iot.yours.com","port":1883 }
client.connect(svr=host)
```
如果服务器设置了用户名和密码，则需要在connect()时传入授权信息，如
```
auth = { "username":"admin","password":"123"}
client.connect(svr=host,auth=auth)
```
调用loop来等待消息到达，当接受到代理发来的消息时，会触发on_message()回调
```
    client.loop()
```
