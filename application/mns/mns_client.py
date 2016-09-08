#coding=utf-8
# Copyright (C) 2015, Alibaba Cloud Computing

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import hashlib
import hmac
import base64
import string
import platform
from . import pkg_info
from  .mns_xml_handler import *
from .mns_exception import *
from .mns_request import *
from .mns_tool import *
from .mns_http import *

URISEC_QUEUE = "queues"
URISEC_MESSAGE = "messages"

URISEC_TOPIC = "topics"
URISEC_SUBSCRIPTION = "subscriptions"

class MNSClient:
    def __init__(self, host, access_id, access_key, version = "2015-06-06", security_token = "", logger=None):
        self.host = self.process_host(host)
        self.access_id = access_id
        self.access_key = access_key
        self.version = version
        self.security_token = security_token
        self.logger = MNSLogger.get_logger() if logger is None else logger
        self.http = MNSHttp(self.host, logger=logger)
        if self.logger:
            self.logger.info("InitClient Host:%s AccessId:%s AccessKey:%s SecurityToken:%s Version:%s" % \
                (host, access_id, access_key, security_token, version))

    def set_log_level(self, log_level):
        MNSLogger.validate_loglevel(log_level)
        self.logger.setLevel(log_level)
        self.http.set_log_level(log_level)

    def set_connection_timeout(self, connection_timeout):
        self.http.set_connection_timeout(connection_timeout)

    def set_keep_alive(self, keep_alive):
        self.http.set_keep_alive(keep_alive)

    def close_connection(self):
        self.http.conn.close()

#===============================================queue operation===============================================#
    def create_queue(self, req, resp):
        #check parameter
        CreateQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_QUEUE, req.queue_name))
        req_inter.data = QueueEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.queue_url = resp.header["Location"]
            if self.logger:
                self.logger.info("CreateQueue RequestId:%s QueueName:%s QueueURL:%s" % \
                    (resp.get_requestid(), req.queue_name, resp.queue_url))

    def delete_queue(self, req, resp):
        #check parameter
        DeleteQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_QUEUE, req.queue_name))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("DeleteQueue RequestId:%s QueueName:%s" % (resp.get_requestid(), req.queue_name))

    def list_queue(self, req, resp):
        #check parameter
        ListQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s" % URISEC_QUEUE)
        if req.prefix != "":
            req_inter.header["x-mns-prefix"] = req.prefix
        if req.ret_number != -1:
            req_inter.header["x-mns-ret-number"] = str(req.ret_number)
        if req.marker != "":
            req_inter.header["x-mns-marker"] = str(req.marker)
        if req.with_meta:
            req_inter.header["x-mns-with-meta"] = "true"
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.queueurl_list, resp.next_marker, resp.queuemeta_list = ListQueueDecoder.decode(resp_inter.data, req.with_meta)
            if self.logger:
                firstQueueURL = "" if resp.queueurl_list == [] else resp.queueurl_list[0]
                lastQueueURL = "" if resp.queueurl_list == [] else resp.queueurl_list[len(resp.queueurl_list)-1]
                self.logger.info("ListQueue RequestId:%s Prefix:%s RetNumber:%s Marker:%s \
                    QueueCount:%s FirstQueueURL:%s LastQueueURL:%s NextMarker:%s" % \
                    (resp.get_requestid(), req.prefix, req.ret_number, req.marker, \
                    len(resp.queueurl_list), firstQueueURL, lastQueueURL, resp.next_marker))

    def set_queue_attributes(self, req, resp):
        #check parameter
        SetQueueAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s?metaoverride=true" % (URISEC_QUEUE, req.queue_name))
        req_inter.data = QueueEncoder.encode(req, False)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response 
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("SetQueueAttributes RequestId:%s QueueName:%s" % (resp.get_requestid(), req.queue_name))

    def get_queue_attributes(self, req, resp):
        #check parameter
        GetQueueAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_QUEUE, req.queue_name))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            queue_attr = GetQueueAttrDecoder.decode(resp_inter.data)
            resp.active_messages = int(queue_attr["ActiveMessages"], 10)
            resp.create_time = int(queue_attr["CreateTime"], 10)
            resp.delay_messages = int(queue_attr["DelayMessages"], 10)
            resp.delay_seconds = int(queue_attr["DelaySeconds"], 10)
            resp.inactive_messages = int(queue_attr["InactiveMessages"], 10)
            resp.last_modify_time = int(queue_attr["LastModifyTime"], 10)
            resp.maximum_message_size = int(queue_attr["MaximumMessageSize"], 10)
            resp.message_retention_period = int(queue_attr["MessageRetentionPeriod"], 10)
            resp.queue_name = queue_attr["QueueName"]
            resp.visibility_timeout = int(queue_attr["VisibilityTimeout"], 10)
            resp.polling_wait_seconds = int(queue_attr["PollingWaitSeconds"], 10)
            if self.logger:
                self.logger.info("GetQueueAttributes RequestId:%s QueueName:%s" % (resp.get_requestid(), req.queue_name))

    def send_message(self, req, resp):
        #check parameter
        SendMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, uri = "/%s/%s/%s" % (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE))
        req_inter.data = MessageEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_id, resp.message_body_md5 = SendMessageDecoder.decode(resp_inter.data)
            if self.logger:
                self.logger.info("SendMessage RequestId:%s QueueName:%s Priority:%s \
                    DelaySeconds:%s MessageId:%s MessageBodyMD5:%s" % \
                    (resp.get_requestid(), req.queue_name, req.priority, \
                    req.delay_seconds, resp.message_id, resp.message_body_md5))

    def batch_send_message(self, req, resp):
        #check parameter
        BatchSendMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, uri = "/%s/%s/%s" % (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE))
        req_inter.data = MessagesEncoder.encode(req.message_list, req.base64encode)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter) 

        #handle result, make response
        resp.status = resp_inter.status 
        resp.header = resp_inter.header 
        self.check_status(resp_inter, resp, BatchSendMessageDecoder)
        if resp.error_data == "":
            resp.message_list = BatchSendMessageDecoder.decode(resp_inter.data)
            if self.logger:
                self.logger.info("BatchSendMessage RequestId:%s QueueName:%s MessageCount:%s MessageInfo\n%s" % \
                    (resp.get_requestid(), req.queue_name, len(req.message_list), \
                    "\n".join(["MessageId:%s MessageBodyMD5:%s" % (msg.message_id, msg.message_body_md5) for msg in resp.message_list])))

    def receive_message(self, req, resp):
        #check parameter
        ReceiveMessageValidator.validate(req)

        #make request internal
        req_url =  "/%s/%s/%s" % (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE)
        if req.wait_seconds != -1:
            req_url += "?waitseconds=%s" % req.wait_seconds
        req_inter = RequestInternal(req.method, req_url)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            data = RecvMessageDecoder.decode(resp_inter.data, req.base64decode)
            self.make_recvresp(data, resp)
            if self.logger:
                self.logger.info("ReceiveMessage RequestId:%s QueueName:%s WaitSeconds:%s MessageId:%s \
                    MessageBodyMD5:%s NextVisibilityTime:%s ReceiptHandle:%s EnqueueTime:%s DequeueCount:%s" % \
                    (resp.get_requestid(), req.queue_name, req.wait_seconds, resp.message_id, \
                    resp.message_body_md5, resp.next_visible_time, resp.receipt_handle, resp.enqueue_time, resp.dequeue_count))

    def batch_receive_message(self, req, resp):
        #check parameter
        BatchReceiveMessageValidator.validate(req)

        #make request internal
        req_url =  "/%s/%s/%s?numOfMessages=%s" % (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE, req.batch_size)
        if req.wait_seconds != -1:
            req_url += "&waitseconds=%s" % req.wait_seconds

        req_inter = RequestInternal(req.method, req_url)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_list = BatchRecvMessageDecoder.decode(resp_inter.data, req.base64decode)
            if self.logger:
                self.logger.info("BatchReceiveMessage RequestId:%s QueueName:%s WaitSeconds:%s BatchSize:%s MessageCount:%s \
                    MessagesInfo\n%s" % (resp.get_requestid(), req.queue_name, req.wait_seconds, req.batch_size, len(resp.message_list),\
                    "\n".join(["MessageId:%s MessageBodyMD5:%s NextVisibilityTime:%s ReceiptHandle:%s EnqueueTime:%s DequeueCount:%s" % \
                                (msg.message_id, msg.message_body_md5, msg.next_visible_time, msg.receipt_handle, msg.enqueue_time, msg.dequeue_count) for msg in resp.message_list])))

    def delete_message(self, req, resp):
        #check parameter
        DeleteMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s?ReceiptHandle=%s" % 
                                                (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE, req.receipt_handle))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("DeleteMessage RequestId:%s QueueName:%s ReceiptHandle:%s" % \
                (resp.get_requestid(), req.queue_name, req.receipt_handle))

    def batch_delete_message(self, req, resp):
        #check parameter
        BatchDeleteMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s" % (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE))
        req_inter.data = ReceiptHandlesEncoder.encode(req.receipt_handle_list)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp, BatchDeleteMessageDecoder)
        if self.logger:
            self.logger.info("BatchDeleteMessage RequestId:%s QueueName:%s ReceiptHandles\n%s" % \
                (resp.get_requestid(), req.queue_name, "\n".join(req.receipt_handle_list)))

    def peek_message(self, req, resp):
        #check parameter
        PeekMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s?peekonly=true" % 
                                                (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            data = PeekMessageDecoder.decode(resp_inter.data, req.base64decode)
            self.make_peekresp(data, resp)
            if self.logger:
                self.logger.info("PeekMessage RequestId:%s QueueName:%s MessageInfo \
                    MessageId:%s BodyMD5:%s EnqueueTime:%s DequeueCount:%s" % \
                    (resp.get_requestid(), req.queue_name, resp.message_id, resp.message_body_md5,\
                     resp.enqueue_time, resp.dequeue_count))

    def batch_peek_message(self, req, resp):
        #check parameter
        BatchPeekMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s?peekonly=true&numOfMessages=%s" % 
                                                (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE, req.batch_size))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_list = BatchPeekMessageDecoder.decode(resp_inter.data, req.base64decode)
            if self.logger:
                self.logger.info("BatchPeekMessage RequestId:%s QueueName:%s BatchSize:%s MessageCount:%s MessageInfo\n%s" % \
                    (resp.get_requestid(), req.queue_name, req.batch_size, len(resp.message_list), \
                     "\n".join(["MessageId:%s BodyMD5:%s EnqueueTime:%s DequeueCount:%s" % \
                        (msg.message_id, msg.message_body_md5, msg.enqueue_time, msg.dequeue_count) for msg in resp.message_list])))

    def change_message_visibility(self, req, resp):
        #check parameter
        ChangeMsgVisValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s?ReceiptHandle=%s&VisibilityTimeout=%d" % 
                                                (URISEC_QUEUE, req.queue_name, URISEC_MESSAGE, req.receipt_handle, req.visibility_timeout))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.receipt_handle, resp.next_visible_time = ChangeMsgVisDecoder.decode(resp_inter.data)
            if self.logger:
                self.logger.info("ChangeMessageVisibility RequestId:%s QueueName:%s ReceiptHandle:%s VisibilityTimeout:%s \
                    NewReceiptHandle:%s NextVisibleTime:%s" % \
                    (resp.get_requestid(), req.queue_name, req.receipt_handle, req.visibility_timeout,\
                     resp.receipt_handle, resp.next_visible_time))


#===============================================topic operation===============================================#
    def create_topic(self, req, resp):
        #check parameter
        CreateTopicValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_TOPIC, req.topic_name))
        req_inter.data = TopicEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.topic_url = resp.header["location"]
            if self.logger:
                self.logger.info("CreateTopic RequestId:%s TopicName:%s TopicURl:%s" % \
                    (resp.get_requestid(), req.topic_name, resp.topic_url))

    def delete_topic(self, req, resp):
        #check parameter
        DeleteTopicValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_TOPIC, req.topic_name))
        self.build_header(req, req_inter)

        #send reqeust
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("DeleteTopic RequestId:%s TopicName:%s" % (resp.get_requestid(), req.topic_name))

    def list_topic(self, req, resp):
        #check parameter
        ListTopicValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s" % URISEC_TOPIC)
        if req.prefix != "":
            req_inter.header["x-mns-prefix"] = req.prefix
        if req.ret_number != -1:
            req_inter.header["x-mns-ret-number"] = str(req.ret_number)
        if req.marker != "":
            req_inter.header["x-mns-marker"] = str(req.marker)
        if req.with_meta:
            req_inter.header["x-mns-with-meta"] = "true"
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.topicurl_list, resp.next_marker, resp.topicmeta_list = ListTopicDecoder.decode(resp_inter.data, req.with_meta)
            first_topicurl = "" if len(resp.topicurl_list) == 0 else resp.topicurl_list[0]
            last_topicurl = "" if len(resp.topicurl_list) == 0 else resp.topicurl_list[len(resp.topicurl_list)-1]
            if self.logger:
                self.logger.info("ListTopic RequestId:%s Prefix:%s RetNumber:%s Marker:%s \
                    TopicCount:%s FirstTopicURL:%s LastTopicURL:%s NextMarker:%s" % \
                    (resp.get_requestid(), req.prefix, req.ret_number, req.marker,\
                     len(resp.topicurl_list), first_topicurl, last_topicurl, resp.next_marker))

    def set_topic_attributes(self, req, resp):
        #check parameter
        SetTopicAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s?metaoverride=true" % (URISEC_TOPIC, req.topic_name))
        req_inter.data = TopicEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("SetTopicAttributes RequestId:%s TopicName:%s" % (resp.get_requestid(), req.topic_name))

    def get_topic_attributes(self, req, resp):
        #check parameter
        GetTopicAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s" % (URISEC_TOPIC, req.topic_name))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            topic_attr = GetTopicAttrDecoder.decode(resp_inter.data)
            resp.message_count = int(topic_attr["MessageCount"], 10)
            resp.create_time = int(topic_attr["CreateTime"], 10)
            resp.last_modify_time = int(topic_attr["LastModifyTime"], 10)
            resp.maximum_message_size = int(topic_attr["MaximumMessageSize"], 10)
            resp.message_retention_period = int(topic_attr["MessageRetentionPeriod"], 10)
            resp.topic_name = topic_attr["TopicName"]
            if self.logger:
                self.logger.info("GetTopicAttributes RequestId:%s TopicName:%s" % (resp.get_requestid(), req.topic_name))

    def publish_message(self, req, resp):
        #check parameter
        PublishMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, uri = "/%s/%s/%s" % (URISEC_TOPIC, req.topic_name, URISEC_MESSAGE))
        req_inter.data = TopicMessageEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_id, resp.message_body_md5 = PublishMessageDecoder.decode(resp_inter.data)
            if self.logger:
                self.logger.info("PublishMessage RequestId:%s TopicName:%s MessageId:%s MessageBodyMD5:%s" % \
                    (resp.get_requestid(), req.topic_name, resp.message_id, resp.message_body_md5))

    def subscribe(self, req, resp):
        #check parameter
        SubscribeValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, uri="/%s/%s/%s/%s" % (URISEC_TOPIC, req.topic_name, URISEC_SUBSCRIPTION, req.subscription_name))
        req_inter.data = SubscriptionEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.subscription_url = resp.header["location"]
            if self.logger:
                self.logger.info("Subscribe RequestId:%s TopicName:%s SubscriptionName:%s SubscriptionURL:%s" % \
                    (resp.get_requestid(), req.topic_name, req.subscription_name, resp.subscription_url))

    def unsubscribe(self, req, resp):
        #check parameter
        UnsubscribeValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s/%s" % (URISEC_TOPIC, req.topic_name, URISEC_SUBSCRIPTION, req.subscription_name))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("Unsubscribe RequestId:%s TopicName:%s SubscriptionName:%s" % (resp.get_requestid(), req.topic_name, req.subscription_name))

    def list_subscription_by_topic(self, req, resp):
        #check parameter
        ListSubscriptionByTopicValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s" % (URISEC_TOPIC, req.topic_name, URISEC_SUBSCRIPTION))
        if req.prefix != "":
            req_inter.header["x-mns-prefix"] = req.prefix
        if req.ret_number != -1:
            req_inter.header["x-mns-ret-number"] = str(req.ret_number)
        if req.marker != "":
            req_inter.header["x-mns-marker"] = req.marker
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.subscriptionurl_list, resp.next_marker = ListSubscriptionByTopicDecoder.decode(resp_inter.data)
            if self.logger:
                first_suburl = "" if len(resp.subscriptionurl_list) == 0 else resp.subscriptionurl_list[0]
                last_suburl = "" if len(resp.subscriptionurl_list) == 0 else resp.subscriptionurl_list[len(resp.subscriptionurl_list)-1]
                self.logger.info("ListSubscriptionByTopic RequestId:%s TopicName:%s Prefix:%s RetNumber:%s \
                    Marker:%s SubscriptionCount:%s FirstSubscriptionURL:%s LastSubscriptionURL:%s" % \
                    (resp.get_requestid(), req.topic_name, req.prefix, req.ret_number, \
                     req.marker, len(resp.subscriptionurl_list), first_suburl, last_suburl))

    def set_subscription_attributes(self, req, resp):
        #check parameter
        SetSubscriptionAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s/%s?metaoverride=true" % (URISEC_TOPIC, req.topic_name, URISEC_SUBSCRIPTION, req.subscription_name))
        req_inter.data = SubscriptionEncoder.encode(req, set=True)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if self.logger:
            self.logger.info("SetSubscriptionAttributes RequestId:%s TopicName:%s SubscriptionName:%s" % \
                (resp.get_requestid(), req.topic_name, req.subscription_name))

    def get_subscription_attributes(self, req, resp):
        #check parameter
        GetSubscriptionAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/%s/%s/%s" % (URISEC_TOPIC, req.topic_name, URISEC_SUBSCRIPTION, req.subscription_name))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.http.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            subscription_attr = GetSubscriptionAttrDecoder.decode(resp_inter.data)
            resp.topic_owner = subscription_attr["TopicOwner"]
            resp.topic_name = subscription_attr["TopicName"]
            resp.subscription_name = subscription_attr["SubscriptionName"]
            resp.endpoint = subscription_attr["Endpoint"]
            resp.notify_strategy = subscription_attr["NotifyStrategy"]
            resp.notify_content_format = subscription_attr["NotifyContentFormat"]
            resp.create_time = int(subscription_attr["CreateTime"], 10)
            resp.last_modify_time = int(subscription_attr["LastModifyTime"], 10)
            if self.logger:
                self.logger.info("GetSubscriptionAttributes RequestId:%s TopicName:%s SubscriptionName:%s" % \
                    (resp.get_requestid(), req.topic_name, req.subscription_name))


###################################################################################################
#----------------------internal-------------------------------------------------------------------#
    def build_header(self, req, req_inter):
        if self.http.is_keep_alive():
            req_inter.header["Connection"] = "Keep-Alive"
        if req_inter.data != "":
            dd = hashlib.md5(req_inter.data).hexdigest()
            req_inter.header["content-md5"] = base64.b64encode(dd.encode('ascii')).decode('ascii')
            req_inter.header["content-type"] = "text/xml;charset=UTF-8"
        req_inter.header["x-mns-version"] = self.version
        req_inter.header["host"] = self.host
        req_inter.header["date"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        req_inter.header["user-agent"] = "aliyun-sdk-python/%s(%s/%s;%s)" % \
                                         (pkg_info.version, platform.system(), platform.release(), platform.python_version())
        req_inter.header["Authorization"] = self.get_signature(req_inter.method, req_inter.header, req_inter.uri)
        if self.security_token != "":
            req_inter.header["security-token"] = self.security_token

    def get_signature(self,method,headers,resource):
        content_md5 = self.get_element('content-md5', headers)
        content_type = self.get_element('content-type', headers)
        date = self.get_element('date', headers)
        canonicalized_resource = resource
        canonicalized_mns_headers = ""
        if len(headers) > 0:
            x_header_list = list(headers.keys())
            x_header_list.sort()
            for k in x_header_list:
                if k.startswith('x-mns-'):
                    canonicalized_mns_headers += k + ":" + headers[k] + "\n"
        string_to_sign = "%s\n%s\n%s\n%s\n%s%s" % (method, content_md5, content_type, date, canonicalized_mns_headers, canonicalized_resource)
        h = hmac.new(self.access_key.encode('ascii'), string_to_sign.encode('ascii'), hashlib.sha1)
        signature = base64.b64encode(h.digest()).decode('ascii')
        signature = "MNS " + self.access_id + ":" + signature
        return signature

    def get_element(self, name, container):
        if name in container:
            return container[name]
        else:
            return ""

    def check_status(self, resp_inter, resp, decoder=ErrorDecoder):
        if resp_inter.status >= 200 and resp_inter.status < 400:
            resp.error_data = ""
        else:
            resp.error_data = resp_inter.data
            if resp_inter.status >= 400 and resp_inter.status <= 600:
                excType, excMessage, reqId, hostId, subErr = decoder.decodeError(resp.error_data)
                if reqId is None:
                    reqId = resp.header["x-mns-request-id"]
                raise MNSServerException(excType, excMessage, reqId, hostId, subErr)
            else:
                raise MNSClientNetworkException("UnkownError", resp_inter.data)

    def make_recvresp(self, data, resp):
        resp.dequeue_count = int(data["DequeueCount"], 10)
        resp.enqueue_time = int(data["EnqueueTime"], 10)
        resp.first_dequeue_time = int(data["FirstDequeueTime"], 10)
        resp.message_body = data["MessageBody"]
        if isinstance(resp.message_body, bytes):
            resp.message_body = resp.message_body.decode('utf8')
        resp.message_id = data["MessageId"]
        resp.message_body_md5 = data["MessageBodyMD5"]
        resp.next_visible_time = int(data["NextVisibleTime"], 10)
        resp.receipt_handle = data["ReceiptHandle"]
        resp.priority = int(data["Priority"], 10)

    def make_peekresp(self, data, resp):
        resp.dequeue_count = int(data["DequeueCount"], 10)
        resp.enqueue_time = int(data["EnqueueTime"], 10)
        resp.first_dequeue_time = int(data["FirstDequeueTime"], 10)
        resp.message_body = data["MessageBody"]
        resp.message_id = data["MessageId"]
        resp.message_body_md5 = data["MessageBodyMD5"]
        resp.priority = int(data["Priority"], 10)

    def process_host(self, host):
        if host.startswith("http://"):
            if host.endswith("/"):
                host =  host[:-1]
            host = host[len("http://"):]
            return host
        else:
            raise MNSClientParameterException("InvalidHost", "Only support http prototol. Invalid host:%s" % host)
