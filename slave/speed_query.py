import time
import threading
from queue import LifoQueue

from slave.comm import CommSender
from slave.decorator import singleton
from slave.models import BaseInfo


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
            q = BaseInfo.objects.all()[0]

            # if is logout or unconnected, only flush queue
            if q.is_log == "False" or q.is_conn == "False":
                while not self.queue.empty():
                    self.queue.get()
                continue

            # else get last item and flush queue
            if not self.queue.empty():
                query = self.queue.get()
                while not self.queue.empty():
                    self.queue.get()
                print(query)
                q.query_speed = query
                q.save()
                r = self.comm_sender.send_msg(data={'type': 'require', 'source': q.room_number, 'speed': query})
                # if query is standby, we should change to standby immediately
                if query == 'standby':
                    q.current_speed = q.query_speed
                    q.query_speed = 'None'
                    q.save()
