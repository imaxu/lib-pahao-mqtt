# -*- coding: utf-8 -*-

# 基于 paho.mqtt 封装的便于调用的帮助库
# Author:xuwh
# http://github.com/imaxu

import paho.mqtt.client as mqtt
import uuid

class MqttAssist:

    client_id = None
    clean_session = None
    userdata = None
    protocol = None
    transport = None
    events = None
    __mqtt_client__ = None


    def __init__(self,clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp"):

        """
        Constructor:
            clean_session
            a boolean that determines the client type. If True, the broker will remove all information about this client when it disconnects. If False, the client is a durable client and subscription information and queued messages will be retained when the client disconnects.
            Note that a client will never discard its own outgoing messages on disconnect. Calling connect() or reconnect() will cause the messages to be resent. Use reinitialise() to reset a client to its original state.

            userdata
            user defined data of any type that is passed as the userdata parameter to callbacks. It may be updated at a later point with the user_data_set() function.

            protocol
            the version of the MQTT protocol to use for this client. Can be either MQTTv31 or MQTTv311

            transport
            set to "websockets" to send MQTT over WebSockets. Leave at the default of "tcp" to use raw TCP.

        """
        self.client_id = str(uuid.uuid1())
        self.clean_session = clean_session
        self.userdata = userdata
        self.protocol = protocol
        self.transport = transport
        self.events = {
            "on_connect":None, 
            "on_message":None,
            "on_publish":None,
            "on_subscribe":None,
            "on_unsubscribe":None,
            "on_disconnect":None
        }
        self.__mqtt_client__ = mqtt.Client(
            client_id=self.client_id,
            clean_session=self.clean_session, 
            userdata=self.userdata, 
            protocol=self.protocol, 
            transport=self.transport)

        self.__mqtt_client__.on_connect = self.__on_connect__

    def __on_connect__(self,client, userdata, flags, rc):
        if self.events["on_connect"]:
            self.events["on_connect"](self, userdata, flags, rc)

    def __on_message__(self,client, userdata, message):
        if self.events["on_message"]:
            self.events["on_message"](self, userdata, message)

    def __on_disconnect__(self,client, userdata, rc):
        if self.events["on_disconnect"]:
            self.events["on_disconnect"](self, userdata, rc)     

    def __on_publish__(self,client, userdata, mid):
        if self.events["on_publish"]:
            self.events["on_publish"](self, userdata, mid)   

    def __on_subscribe__(self,client, userdata, mid, granted_qos):
        if self.events["on_subscribe"]:
            self.events["on_subscribe"](self,  userdata, mid, granted_qos)      

    def __on_unsubscribe__(self,client, userdata, mid):
        if self.events["on_unsubscribe"]:
            self.events["on_unsubscribe"](self,  userdata, mid)                        

    def event(self,event_name,callback):
        """
        attach callback on mqtt client:
            We hidden some callback functions from paho.mqtt,because less bussiness.
            So,this include on_connect,on_message,on_publish,on_subscribe,on_unsubscribe,message_callback_add.
            You can dir(instance) to see the details.

            p.s you can also add event by instance.events.event_name = yourFunction

            on_connect()
                on_connect(client, userdata, flags, rc)

            on_disconnect()
                on_disconnect(client, userdata, rc)                

            on_message()
                on_message(client, userdata, message)

            on_publish()
                on_publish(client, userdata, mid)

            on_subscribe()
                on_subscribe(client, userdata, mid, granted_qos)

            on_unsubscribe()
                on_unsubscribe(client, userdata, mid)
        """
        if callback and event_name in self.events.keys():
            self.events[event_name] = callback
            if hasattr(self.__mqtt_client__,event_name) and hasattr(self,"__" + event_name + "__"):
                setattr(self.__mqtt_client__,event_name,eval("self.__" + event_name + "__"))


    def filter(self,topic,callback):
        """

        This function allows you to define callbacks that handle incoming messages for specific subscription filters, 
        including with wildcards. 
        This lets you, for example, 
        subscribe to sensors/# and have one callback to handle sensors/temperature and another to handle sensors/humidity.

            topic
            the subscription filter to match against for this callback. Only one callback may be defined per literal sub string
            callback
            the callback to be used. Takes the same form as the on_message callback.   

        """
        self.__mqtt_client__.message_callback_add(topic,callback)


    def filter_remove(self,topic):
        """
        Remove a topic/subscription specific callback previously registered using filter().
            sub
            the subscription filter to remove
        """
        self.__mqtt_client__.message_callback_remove(topic)


    def connect(self,auth={},svr={}):

        """
        The connect() function connects the client to a broker. 
        This is a blocking function. It takes the following arguments::
            auth
            this is a dict object that is defined name,pwd
            example: { username="user",password="12345"}

            svr
            this is a dict object that is defined host,port
            example:{host="iot.xxx.com",port=1883}
        """
        self.__mqtt_client__.username_pw_set(auth["username"],auth["password"])
        self.__mqtt_client__.connect(svr["host"],svr["port"],60)


    def subscribe(self,topic, qos=0):
        """
        Subscribe the client to one or more topics.
        This function may be called in three different ways:
            topic
            a string specifying the subscription topic to subscribe to.
            qos
            the desired quality of service level for the subscription. Defaults to 0.
            e.g. subscribe("my/topic", 2)
            e.g. subscribe(("my/topic", 1))
            e.g. subscribe([("my/topic", 0), ("another/topic", 2)])
        """
        self.__mqtt_client__.subscribe(topic,qos)


    def unsubscribe(self,topic):
        """
        Unsubscribe the client from one or more topics.
            topic
            a single string, or list of strings that are the subscription topics to unsubscribe from.
        """
        self.__mqtt_client__.unsubscribe(topic)


    def publish(self,topic, payload=None, qos=0, retain=False):
        """
        This causes a message to be sent to the broker and subsequently from the broker to any clients subscribing to matching topics. 
        It takes the following arguments:

            topic
            the topic that the message should be published on
            payload
            the actual message to send. If not given, or set to None a zero length message will be used. Passing an int or float will result in the payload being converted to a string representing that number. If you wish to send a true int/float, use struct.pack() to create the payload you require
            qos
            the quality of service level to use
            retain
            if set to True, the message will be set as the "last known good"/retained message for the topic.        
        """

        self.__mqtt_client__.publish(topic, payload, qos, retain)
        pass
    
    def easy_publish(self,topic, 
    payload=None, qos=0, retain=False, 
    hostname="localhost",port=1883,keepalive=60, will=None, auth=None, tls=None):
        """
        This module provides some helper functions to allow straightforward publishing of messages in a one-shot manner. 
        In other words, they are useful for the situation where you have a single/multiple messages you want to publish to a broker, 
        then disconnect with nothing else required.
        arguments：
            topic
            the only required argument must be the topic string to which the payload will be published.

            payload
            the payload to be published. If "" or None, a zero length payload will be published.

            qos
            the qos to use when publishing, default to 0.

            retain
            set the message to be retained (True) or not (False).

            hostname
            a string containing the address of the broker to connect to. Defaults to localhost.

            port
            the port to connect to the broker on. Defaults to 1883.

            keepalive
            the keepalive timeout value for the client. Defaults to 60 seconds.

            will
            a dict containing will parameters for the client:
            will = {'topic': "<topic>", 'payload':"<payload">, 'qos':<qos>, 'retain':<retain>}.
            Topic is required, all other parameters are optional and will default to None, 0 and False respectively.
            Defaults to None, which indicates no will should be used.

            auth
            a dict containing authentication parameters for the client:

            auth = {'username':"<username>", 'password':"<password>"}
            Username is required, password is optional and will default to None if not provided.
            Defaults to None, which indicates no authentication is to be used.

            tls
            a dict containing TLS configuration parameters for the client:

            dict = {'ca_certs':"<ca_certs>", 'certfile':"<certfile>", 'keyfile':"<keyfile>", 'tls_version':"<tls_version>", 'ciphers':"<ciphers">}
            ca_certs is required, all other parameters are optional and will default to None if not provided, which results in the client using the default behaviour - see the paho.mqtt.client documentation.
            Defaults to None, which indicates that TLS should not be used.
        """
        import paho.mqtt.publish as publish
        publish.single(topic, payload, qos, retain, hostname,port, self.client_id, keepalive, will, auth, tls,self.protocol, self.transport)

    def easy_multiple(self,msgs, hostname="localhost", port=1883, keepalive=60,will=None, auth=None, tls=None):
        """
        Publish multiple messages to a broker, then disconnect cleanly.
        arguments：
            msgs
            a list of messages to publish. Each message is either a dict or a tuple.
            If a dict, only the topic must be present. Default values will be used for any missing arguments. The dict must be of the form:
            msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>, 'retain':<retain>}
            topic must be present and may not be empty. If payload is "", None or not present then a zero length payload will be published. If qos is not present, the default of 0 is used. If retain is not present, the default of False is used.
            If a tuple, then it must be of the form:
            ("<topic>", "<payload>", qos, retain)

            See easy_publish() for the description of hostname, port, keepalive, will, auth, tls.

            e.g:
            msgs = [{'topic':"paho/test/multiple", 'payload':"multiple 1"},
                ("paho/test/multiple", "multiple 2", 0, False)]
            easy_multiple(msgs, hostname="iot.eclipse.org")            
        """
        import paho.mqtt.publish as publish
        publish.multiple(msgs,  hostname, port, keepalive,will, auth, tls)

    def easy_subscribe(self,topics, qos=0, msg_count=1, 
    retained=False, hostname="localhost",port=1883, keepalive=60, will=None, auth=None, tls=None):
        """
        Subscribe to a set of topics and return the messages received. This is a blocking function.
        arguments：
            topics
            the only required argument is the topic string to which the client will subscribe. 
            This can either be a string or a list of strings if multiple topics should be subscribed to.

            qos
            the qos to use when subscribing, defaults to 0.

            msg_count
            the number of messages to retrieve from the broker. 
            Defaults to 1. If 1, a single MQTTMessage object will be returned. If >1, a list of MQTTMessages will be returned.

            retained
            set to True to consider retained messages, set to False to ignore messages with the retained flag set.

            hostname
            a string containing the address of the broker to connect to. Defaults to localhost.

            port
            the port to connect to the broker on. Defaults to 1883.

            keepalive
            the keepalive timeout value for the client. Defaults to 60 seconds.

            will
            a dict containing will parameters for the client:
            will = {'topic': "<topic>", 'payload':"<payload">, 'qos':<qos>, 'retain':<retain>}.
            Topic is required, all other parameters are optional and will default to None, 0 and False respectively.
            Defaults to None, which indicates no will should be used.

            auth
            a dict containing authentication parameters for the client:
            auth = {'username':"<username>", 'password':"<password>"}
            Username is required, password is optional and will default to None if not provided.
            Defaults to None, which indicates no authentication is to be used.

            tls
            a dict containing TLS configuration parameters for the client:
            dict = {'ca_certs':"<ca_certs>", 'certfile':"<certfile>", 'keyfile':"<keyfile>", 'tls_version':"<tls_version>", 'ciphers':"<ciphers">}
            ca_certs is required, all other parameters are optional and will default to None if not provided, which results in the client using the default behaviour - see the paho.mqtt.client documentation.
            Defaults to None, which indicates that TLS should not be used.    
        """

        import paho.mqtt.subscribe as subscribe
        subscribe.simple(topics,qos, msg_count, retained, hostname,port, 
        self.client_id, keepalive, will, auth, tls,self.protocol)

    def easy_multi_subscribe(self,callback, topics, qos=0, userdata=None, hostname="localhost",port=1883, 
    keepalive=60, will=None, auth=None, tls=None):
        """
        Subscribe to a set of topics and process the messages received using a user provided callback.
        arguments:
            callback
            an "on_message" callback that will be used for each message received, and of the form
            def on_message(client, userdata, message)

            topics
            the topic string to which the client will subscribe. 
            This can either be a string or a list of strings if multiple topics should be subscribed to.

            qos
            the qos to use when subscribing, defaults to 0.

            userdata
            a user provided object that will be passed to the on_message callback when a message is received.
            See easy_subscribe() for the description of hostname, port, keepalive, will, auth, tls.        
        """

        import paho.mqtt.subscribe as subscribe
        subscribe.callback(callback, topics, qos, userdata, hostname,port, 
        self.client_id, keepalive, will, auth, tls,self.protocol)

    def loop(self):
        """
        """

        try:
            self.__mqtt_client__.loop_forever()
        except KeyboardInterrupt:
            SystemExit



    