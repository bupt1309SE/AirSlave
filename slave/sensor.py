import time
import threading

from slave.decorator import singleton
from slave.models import BaseInfo
from slave.speed_query import QueryQueue


@singleton
class Sensor:
    def __init__(self):
        self.query_queue = QueryQueue()
        self.last_query = 'None'
        th = threading.Thread(target=self.simulate)
        th.start()

    # simulate temp change
    def simulate(self):
        while True:
            time.sleep(1)
            q = BaseInfo.objects.all()[0]
            if q.is_log == 'False' or q.is_conn =='False':
                continue
            if q.mode == 'cold':
                if q.current_speed == 'standby':
                    if q.current_temp < 25:
                        q.current_temp += 0.01
                    if q.current_temp >= q.target_temp + 1 and self.last_query != 'None':
                        self.query_queue.put(self.last_query)
                        self.last_query = 'None'
                else:
                    if q.current_temp > 18:
                        if q.current_speed == 'low':
                            q.current_temp -= 0.01
                        elif q.current_speed == 'medium':
                            q.current_temp -= 0.02
                        elif q.current_speed == 'high':
                            q.current_temp -= 0.03
                        if q.current_temp <= q.target_temp and self.last_query == 'None':
                            self.query_queue.put('standby')
                            self.last_query = q.current_speed
            else:
                if q.current_speed == 'standby':
                    if q.current_temp > 25:
                        q.current_temp -= 0.01
                    if q.current_temp < q.target_temp - 1 and self.last_query != 'None':
                        self.query_queue.put(self.last_query)
                        self.last_query = 'None'
                else:
                    if q.current_temp < 30:
                        if q.current_speed == 'low':
                            q.current_temp += 0.01
                        elif q.current_speed == 'medium':
                            q.current_temp += 0.02
                        elif q.current_speed == 'high':
                            q.current_temp += 0.03
                        if q.current_temp >= q.target_temp and self.last_query == 'None':
                            self.query_queue.put('standby')
                            self.last_query = q.current_speed;
            q.save()
