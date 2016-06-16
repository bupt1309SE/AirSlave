from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from slave.comm import CommSender
from slave.cost_query import CostQuery
from slave.models import ConnInfo, CostInfo, QueryInfo, SensorInfo, ModeInfo, SettingInfo, RoomInfo
from slave.sensor import Sensor
from slave.speed_query import QueryQueue

# initialize all info
c = ConnInfo.objects.all()[0]
c.is_log = 'False'
c.is_conn = 'False'
c.save()

c = CostInfo.objects.all()[0]
c.power_price = 5.0
c.total_cost = 0.0
c.power_consump = 0.0
c.save()

q = QueryInfo.objects.all()[0]
q.current_speed = 'standby'
q.query_speed = 'None'
q.save()

s = SensorInfo.objects.all()[0]
s.current_temp = 25.0
s.save()

# create all threads
comm_sender = CommSender()
query_queue = QueryQueue()
sensor = Sensor()
cost_queryer = CostQuery()


# Create your views here.

# index view  to show all information
def index(request):
    return render(request, 'slave/index.html')


@csrf_exempt
def get_info(request):
    q = QueryInfo.objects.all()[0]
    m = ModeInfo.objects.all()[0]
    s = SettingInfo.objects.all()[0]
    ss = SensorInfo.objects.all()[0]
    c = CostInfo.objects.all()[0]
    cc = ConnInfo.objects.all()[0]
    return JsonResponse({'current_speed': q.current_speed,
                         'mode': m.mode,
                         'target_temp': s.target_temp,
                         'current_temp': ss.current_temp,
                         'query_speed': q.query_speed,
                         'power_consump': c.power_consump,
                         'power_price': c.power_price,
                         'total_cost': c.total_cost,
                         'is_log': cc.is_log,
                         'is_conn': cc.is_conn})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        res = comm_sender.connect_to_host(request.POST['ip'], request.POST['port'], request.POST['room_number'],
                                          request.get_host())
        return HttpResponse(res)


@csrf_exempt
def logout(request):
    q = RoomInfo.objects.all()[0]
    r = comm_sender.send_msg(data={'type': 'logout', 'source': q.room_number})
    try:
        js = r.json()
        if js['ack_nak'] == 'ACK':
            q.is_log = 'False'
            q.is_conn = 'False'
            q.current_speed = 'standby'
            q.save()
            return HttpResponse(1)
        else:
            return HttpResponse(0)
    except:
        return HttpResponse(0)


# target_temp reply
# update target temperature
@csrf_exempt
def target_reply(request):
    if request.method == 'POST':
        q = SettingInfo.objects.all()[0]
        q.target_temp = float(request.POST['target_temp'])
        q.save()
        m = ModeInfo.objects.all()[0]
        s = SensorInfo.objects.all()[0]
        if m.mode == 'cold' and q.target_temp > s.current_temp:
            query_queue.put('standby')
        elif m.mode == 'hot' and q.target_temp < s.current_temp:
            query_queue.put('standby')
        return HttpResponse(1)


# query speed_reply
# insert query into query_queue
@csrf_exempt
def speed_reply(request):
    if request.method == 'POST':
        query_queue.put(request.POST['speed_choice'])
        return HttpResponse(1)


# host to check current and target_temperature
# return a json type with current and target temperature
def host_check_temperature(request):
    r = RoomInfo.objects.all()[0]
    s = SensorInfo.objects.all()[0]
    ss = SettingInfo.objects.all()[0]

    return JsonResponse(
        {'type': 'check_temperature', 'source': r.room_number, 'ack_nak': 'ACK', 'room_temperature': s.current_temp,
         'setting_temperature': ss.target_temp})


# host send  'stop' message
# slave state change to standby
# return a json with ACK
def stop_service(request):
    r = RoomInfo.objects.all()[0]
    q = QueryInfo.objects.all()[0]
    q.speed = 'standby'
    q.save()
    return JsonResponse({'type': 'stop', 'source': r.room_number, 'ack_nak': 'ACK'})


# host send 'start' message
# slave change state to the latest query which is in database
# and query_speed should remove
def start_service(request):
    q = QueryInfo.objects.all()[0]
    r = RoomInfo.objects.all()[0]
    if q.query_speed != 'None':
        q.current_speed = q.query_speed
        q.query_speed = 'None'
        q.save()
    return JsonResponse({'type': 'send', 'source': r.room_number, 'ack_nak': 'ACK'})


@csrf_exempt
# communication view
# deal with communication with host
def communication(request):
    if request.method == 'POST':
        if request.POST['type'] == 'check_temperature' and request.POST['source'] == 'host':
            return host_check_temperature(request)
        elif request.POST['type'] == 'send' and request.POST['source'] == 'host':
            return start_service(request)
        elif request.POST['type'] == 'stop' and request.POST['source'] == 'host':
            return stop_service(request)
    return JsonResponse({'ack_nak': 'NAK'})
