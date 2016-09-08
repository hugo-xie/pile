import json
from .account import Account
from .queue import QueueMeta, Message
from .mns_exception import MNSServerException

def get_or_create_queue(account, sn, meta=None):
    if not meta:
        meta = QueueMeta()
    queue = account.get_queue("PileQueue-%s" % sn)
    queue.create(meta)
    return queue

def poll_queue(queue, wait_seconds=-1):
    try:
        msg = queue.receive_message(wait_seconds)
    except MNSServerException as ex:
        if len(ex.args) < 1 or ex.args[0] != 'MessageNotExist':
            print('cannot receive message from queue', queue)
            print(' ', str(ex))
        return None
    try:
        json_data = json.loads(msg.message_body)
        if not isinstance(json_data, dict):
            json_data = None
    except:
        json_data = None
    finally:
        setattr(msg, 'json', json_data)

    return msg

def send_queue_msg(queue, content, msg=None):
    if msg is None:
        msg = Message()
    msg.message_body = content
    return queue.send_message(msg)

def ack_queue_msg(queue, msg):
    queue.delete_message(msg.receipt_handle)

assert(Account) # eliminate lint unused import warning
