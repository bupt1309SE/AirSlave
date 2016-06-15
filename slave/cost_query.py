import threading
import time

from slave.comm import CommSender
from slave.decorator import singleton
from slave.models import BaseInfo


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
            q = BaseInfo.objects.all()[0]

            # if log out or can't connect, don't send message
            if q.is_log == 'False' or q.is_conn == "False":
                continue
            r = self.comm_sender.send_msg(data={'type': 'query_cost', 'source': q.room_number})

            js = r.json()
            q.power_consump = js['power_consumption']
            q.power_price = js['price']
            q.total_cost = js['total_cost']
            q.save()
