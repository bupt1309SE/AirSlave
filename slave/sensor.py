import threading
import time

from slave.decorator import singleton
from slave.models import RoomInfo, SensorInfo, ConnInfo, ModeInfo, QueryInfo, SettingInfo
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
            q = RoomInfo.objects.all()[0]
            c = ConnInfo.objects.all()[0]
            m = ModeInfo.objects.all()[0]
            qq = QueryInfo.objects.all()[0]
            s = SensorInfo.objects.all()[0]
            ss = SettingInfo.objects.all()[0]
            if c.is_log == 'False' or c.is_conn == 'False':
                continue
            if m.mode == 'cold':
                if qq.current_speed == 'standby':
                    if s.current_temp < 25:
                        s.current_temp += 0.01
                    if s.current_temp >= ss.target_temp + 1 and self.last_query != 'None':
                        self.query_queue.put(self.last_query)
                        self.last_query = 'None'
                else:
                    if s.current_temp > 18:
                        if qq.current_speed == 'low':
                            s.current_temp -= 0.01
                        elif qq.current_speed == 'medium':
                            s.current_temp -= 0.02
                        elif qq.current_speed == 'high':
                            s.current_temp -= 0.03
                        if s.current_temp <= ss.target_temp and self.last_query == 'None':
                            self.query_queue.put('standby')
                            self.last_query = qq.current_speed
            else:
                if qq.current_speed == 'standby':
                    if s.current_temp > 25:
                        s.current_temp -= 0.01
                    if s.current_temp < ss.target_temp - 1 and self.last_query != 'None':
                        self.query_queue.put(self.last_query)
                        self.last_query = 'None'
                else:
                    if s.current_temp < 30:
                        if qq.current_speed == 'low':
                            s.current_temp += 0.01
                        elif qq.current_speed == 'medium':
                            s.current_temp += 0.02
                        elif qq.current_speed == 'high':
                            s.current_temp += 0.03
                        if s.current_temp >= ss.target_temp and self.last_query == 'None':
                            self.query_queue.put('standby')
                            self.last_query = qq.current_speed
            s.save()
