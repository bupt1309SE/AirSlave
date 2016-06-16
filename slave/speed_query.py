import time
import threading
from queue import LifoQueue

from slave.comm import CommSender
from slave.decorator import singleton
from slave.models import RoomInfo,ConnInfo,QueryInfo,ModeInfo,SettingInfo,SensorInfo


# query_queue stored temp speed_choice
# every second, choose the latest speed_choice and sending to host
# after receive host 'send' or 'stop'  message, update  current_speed


@singleton
class QueryQueue:
    def __init__(self):
        self.queue = LifoQueue()
        self.comm_sender = CommSender()
        th = threading.Thread(target=self.send_require)
        th.start()

    def put(self, item):
        self.queue.put(item)

    def send_require(self):
        while True:
            time.sleep(1)
            c = ConnInfo.objects.all()[0]
            q = QueryInfo.objects.all()[0]
            r = RoomInfo.objects.all()[0]
            # if is logout or unconnected, only flush queue
            if c.is_log == "False" or c.is_conn == "False":
                while not self.queue.empty():
                    self.queue.get()
                continue

            # else get last item and flush queue
            if not self.queue.empty():
                query = self.queue.get()
                while not self.queue.empty():
                    self.queue.get()
                #
                m = ModeInfo.objects.all()[0]
                s = SensorInfo.objects.all()[0]
                ss = SettingInfo.objects.all()[0]
                if m.mode == 'cold' and ss.target_temp > s.current_temp:
                    query = 'standby'
                elif m.mode == 'hot' and ss.target_temp < s.current_temp:
                    query = 'standby'
                #
                q.query_speed = query
                q.save()
                r = self.comm_sender.send_msg(data={'type': 'require', 'source': r.room_number, 'speed': query})
                # if query is standby, we should change to standby immediately
                if query == 'standby' and r.json()['ack_nak'] == 'ACK':
                    q.current_speed = 'standby'
                    q.query_speed = 'None'
                    q.save()
