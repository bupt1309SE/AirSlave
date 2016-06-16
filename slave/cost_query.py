import threading
import time

from slave.comm import CommSender
from slave.decorator import singleton
from slave.models import RoomInfo,CostInfo,ConnInfo


@singleton
class CostQuery:
    def __init__(self):
        self.comm_sender = CommSender()
        th = threading.Thread(target=self.cost_query)
        th.start()

    # get cost from host
    def cost_query(self):
        while True:
            time.sleep(1)
            q = RoomInfo.objects.all()[0]
            l = ConnInfo.objects.all()[0]
            c = CostInfo.objects.all()[0]
            # if log out or can't connect, don't send message
            if l.is_log == 'False' or l.is_conn == "False":
                continue
            r = self.comm_sender.send_msg(data={'type': 'query_cost', 'source': q.room_number})

            js = r.json()
            c.power_consump = js['power_consumption']
            c.power_price = js['price']
            c.total_cost = js['total_cost']
            c.save()
