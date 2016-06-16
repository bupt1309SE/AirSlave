import threading
import time

import requests
import requests.exceptions

from slave.decorator import singleton
from slave.models import ConnInfo,RoomInfo,ModeInfo


@singleton
class CommSender:
    def __init__(self):
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
                q = RoomInfo.objects.all()[0]
                q.room_number = room_number
                q.save()
                self.host_url = url
                r = ConnInfo.objects.all()[0]
                r.is_log = 'True'
                r.save()
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
            q = RoomInfo.objects.all()[0]
            c = ConnInfo.objects.all()[0]
            m = ModeInfo.objects.all()[0]
            if c.is_log == "False":
                continue
            try:
                r = requests.post(self.host_url, data={'type': 'query_mode', 'source': q.room_number}, timeout=2)
                js = r.json()
                m.mode = js['mode']
                m.save()
                c.is_conn = 'True'
                c.save()
            except:
                c.is_conn = 'False'
                c.save()
