import threading
import time

import requests
import requests.exceptions

from slave.decorator import singleton
from slave.models import BaseInfo


@singleton
class CommSender:
    def __init__(self):
        q = BaseInfo.objects.all()[0]
        self.host_url = ''
        th = threading.Thread(target=self.test_connection)
        th.start()

    # send message to host
    def send_msg(self, data):
        r = requests.post(self.host_url, data=data)
        return r

    def connect_to_host(self, ip, port, room_number, my_host):
        url = 'http://' + ip + ":" + port + '/communication'
        try:
            r = requests.post(url, data={'type': 'login', 'source': room_number, 'ip_port': 'http://' + my_host},
                              timeout=2)
            js = r.json()
            if js['ack_nak'] == 'ACK':
                q = BaseInfo.objects.all()[0]
                q.room_number = room_number
                self.host_url = url
                q.is_log = 'True'
                q.save()
                return 1
            else:
                return 0
        except:
        #except requests.exceptions.Timeout:
            return 0

    # test whether can connect to host by mode_query
    def test_connection(self):
        while True:
            time.sleep(1)
            q = BaseInfo.objects.all()[0]
            if q.is_log == "False":
                continue
            try:
                r = requests.post(self.host_url, data={'type': 'query_mode', 'source': q.room_number}, timeout=2)
                js = r.json()
                q.mode = js['mode']
                q.is_conn = 'True'
                q.save()
            except requests.exceptions.Timeout:
                q.is_conn = 'False'
                q.save()
