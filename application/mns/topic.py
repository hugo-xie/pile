#coding=utf-8
# Copyright (C) 2015, Alibaba Cloud Computing

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
from .mns_client import MNSClient
from .mns_request import *
from .mns_exception import *
from .subscription import *

class Topic:
    def __init__(self, topic_name, mns_client, debug=False):
        self.topic_name = topic_name
        self.mns_client = mns_client
        self.debug = debug

    def set_debug(self, debug):
        self.debug = debug

    def get_subscription(self, subscription_name):
        """ 获取Topic的一个Subscription对象

            @type subscription_name: string
            @param subscription_name: 订阅名称

            @rtype: Subscription object
            @return: 返回该Topic的一个Subscription对象
        """
        return Subscription(self.topic_name, subscription_name, self.mns_client, self.debug)

    def create(self, topic_meta):
        """ 创建主题

            @type topic_meta: TopicMeta object
            @param topic_meta: TopicMeta对象，指定主题的属性

            @rtype: string
            @return 新创建队列的URL

            @note: Exception
            :: MNSClientParameterException  参数格式异常
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = CreateTopicRequest(self.topic_name, topic_meta.maximum_message_size)
        resp = CreateTopicResponse()
        self.mns_client.create_topic(req, resp)
        self.debuginfo(resp)
        return resp.topic_url

    def get_attributes(self):
        """ 获取主题属性

            @rtype: TopicMeta object
            @return 主题的属性

            @note: Exception
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = GetTopicAttributesRequest(self.topic_name)
        resp = GetTopicAttributesResponse()
        self.mns_client.get_topic_attributes(req, resp)
        topic_meta = TopicMeta()
        self.__resp2meta__(topic_meta, resp)
        self.debuginfo(resp)
        return topic_meta

    def set_attributes(self, topic_meta):
        """ 设置队列属性

            @type topic_meta: TopicMeta object
            @param topic_meta: 新设置的主题属性

            @note: Exception
            :: MNSClientParameterException  参数格式异常
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = SetTopicAttributesRequest(self.topic_name, topic_meta.maximum_message_size)
        resp = SetTopicAttributesResponse()
        self.mns_client.set_topic_attributes(req, resp)
        self.debuginfo(resp)

    def delete(self):
        """ 删除主题

            @note: Exception
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = DeleteTopicRequest(self.topic_name)
        resp = DeleteTopicResponse()
        self.mns_client.delete_topic(req, resp)
        self.debuginfo(resp)

    def publish_message(self, message):
        """ 发送消息

            @type message: TopicMessage object
            @param message: 发布的TopicMessage object

            @rtype: TopicMessage object
            @return: 消息发布成功的返回属性，包含MessageId和MessageBodyMD5

            @note: Exception
            :: MNSClientParameterException  参数格式异常
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = PublishMessageRequest(self.topic_name, message.message_body)
        resp = PublishMessageResponse()
        self.mns_client.publish_message(req, resp)
        self.debuginfo(resp)
        return self.__publish_resp2msg__(resp)

    def list_subscription(self, prefix = "", ret_number = -1, marker = ""):
        """ 列出该主题的订阅

            @type prefix: string
            @param prefix: 订阅名称的前缀

            @type ret_number: int
            @param ret_number: list_subscription最多返回的订阅个数

            @type marker: string
            @param marker: list_subscriptiond的起始位置，上次list_subscription返回的next_marker

            @rtype: tuple
            @return SubscriptionURL的列表,下次list subscription的起始位置;当所有订阅都返回时，next_marker为""

            @note: Exception
            :: MNSClientParameterException  参数格式异常
            :: MNSClientNetworkException    网络异常
            :: MNSServerException           mns处理异常
        """
        req = ListSubscriptionByTopicRequest(self.topic_name, prefix, ret_number, marker)
        resp = ListSubscriptionByTopicResponse()
        self.mns_client.list_subscription_by_topic(req, resp)
        self.debuginfo(resp)
        return resp.subscriptionurl_list, resp.next_marker

    def debuginfo(self, resp):
        if self.debug:
            print("===================DEBUG INFO===================")
            print("RequestId: %s" % resp.header["x-mns-request-id"])
            print("================================================")

    def __resp2meta__(self, topic_meta, resp):
        topic_meta.message_count = resp.message_count
        topic_meta.create_time = resp.create_time
        topic_meta.last_modify_time = resp.last_modify_time
        topic_meta.maximum_message_size = resp.maximum_message_size
        topic_meta.message_retention_period = resp.message_retention_period
        topic_meta.topic_name = resp.topic_name

    def __publish_resp2msg__(self, resp):
        msg = TopicMessage()
        msg.message_id = resp.message_id
        msg.message_body_md5 = resp.message_body_md5
        return msg

class TopicMeta:
    def __init__(self, maximum_message_size = -1):
        """ 主题属性
            @note：设置属性
            :: maximum_message_size: message body的最大长度，单位：Byte

            @note: 不可设置属性
            :: message_retention_period: message最长存活时间，单位：秒
            :: message_count: topic中的消息数
            :: create_time: topic创建时间，单位：秒
            :: last_modify_time: 修改topic属性的最近时间，单位：秒
            :: topic_name: 主题名称
        """
        self.maximum_message_size = maximum_message_size
        self.message_retention_period = -1
        self.message_count = -1
        self.create_time = -1
        self.last_modify_time = -1
        self.topic_name = ""

    def set_maximum_message_size(self, maximum_message_size):
        self.maximum_message_size = maximum_message_size

    def __str__(self):
        meta_info = {"MaximumMessageSize": self.maximum_message_size,
                     "MessageRetentionPeriod": self.message_retention_period,
                     "MessageCount": self.message_count,
                     "CreateTime": time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(self.create_time)),
                     "LastModifyTime": time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(self.last_modify_time)),
                     "TopicName": self.topic_name}
        return "\n".join(["%s: %s" % (k.ljust(30),v) for k,v in list(meta_info.items())])

class TopicMessage:
    def __init__(self, message_body = ""):
        """ 消息属性

            @note: publish_message 指定属性
            :: message_body             消息体

            @note: publish_message 返回属性
            :: message_id               消息ID
            :: message_body_md5         消息体的MD5值
        """
        self.message_body = message_body

        self.message_id = ""
        self.message_body_md5 = ""

    def set_messagebody(self, message_body):
        self.message_body = message_body
