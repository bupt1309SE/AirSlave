from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from slave.comm import CommSender
from slave.cost_query import CostQuery
from slave.forms import HostForm, RoomNumberForm, TargetTempForm, SpeedForm
from slave.models import BaseInfo
from slave.sensor import Sensor
from slave.speed_query import QueryQueue

# initialize all info
q = BaseInfo.objects.all()[0]
q.is_log = 'False'
q.is_conn = 'False'
q.current_temp = 25.0
q.current_speed = 'standby'
q.query_speed = 'None'
q.save()

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
    q = BaseInfo.objects.all()[0]
    return JsonResponse({'current_speed': q.current_speed,
                         'mode': q.mode,
                         'target_temp': q.target_temp,
                         'current_temp': q.current_temp,
                         'query_speed': q.query_speed,
                         'power_consump': q.power_consump,
                         'power_price': q.power_price,
                         'total_cost': q.total_cost,
                         'is_log': q.is_log,
                         'is_conn': q.is_conn})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        res = comm_sender.connect_to_host(request.POST['ip'], request.POST['port'], request.POST['room_number'],
                                          request.get_host())
        return HttpResponse(res)


@csrf_exempt
def logout(request):
    q = BaseInfo.objects.all()[0]
    r = comm_sender.send_msg(data={'type': 'logout', 'source': q.room_number})
    js = r.json()
    if js['ack_nak'] == 'ACK':
        q.is_log = 'False'
        q.is_conn = 'False'
        q.current_speed = 'standby'
        q.save()
    return HttpResponse(1)


def mode_reply(request):
    q = BaseInfo.objects.all()[0]
    r = comm_sender.send_msg(data={'type': 'query_mode', 'source': q.room_number})
    return HttpResponse(r.text)


def setting(request):
    q = BaseInfo.objects.all()[0]
    host_form = HostForm({'ip_address': q.host_ip, 'port_address': q.host_port})
    room_form = RoomNumberForm({'room_number': q.room_number})
    target_temp_form = TargetTempForm({'target_temp': q.target_temp})
    speed_form = SpeedForm({'speed_choice': q.current_speed})
    return render(request, 'slave/setting.html', {
        'host_form': host_form,
        'room_form': room_form,
        'target_temp_form': target_temp_form,
        'speed_form': speed_form})


# host_reply view
# update host_ip  and host_port
def host_reply(request):
    if request.method == 'POST':
        form = HostForm(request.POST)
        if form.is_valid():
            q = BaseInfo.objects.all()[0]
            q.host_ip = form.cleaned_data['ip_address']
            q.host_port = form.cleaned_data['port_address']
            q.save()
            return HttpResponseRedirect(reverse('slave:index'))
        else:
            return HttpResponse('Error')


# room_reply
# update room_number
def room_reply(request):
    if request.method == 'POST':
        form = RoomNumberForm(request.POST)
        if form.is_valid():
            q = BaseInfo.objects.all()[0]
            q.room_number = form.cleaned_data['room_number']
            q.save()
            return HttpResponseRedirect(reverse('slave:index'))
        else:
            return HttpResponse('Error')


# target_temp reply
# update target temperature
@csrf_exempt
def target_reply(request):
    if request.method == 'POST':
        q = BaseInfo.objects.all()[0]
        q.target_temp = request.POST['target_temp']
        q.save()
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
    q = BaseInfo.objects.all()[0]
    return JsonResponse(
        {'type': 'check_temperature', 'source': q.room_number, 'ack_nak': 'ACK', 'room_temperature': q.current_temp,
         'setting_temperature': q.target_temp})


# host send  'stop' message
# slave state change to standby
# return a json with ACK
def stop_service(request):
    q = BaseInfo.objects.all()[0]
    q.speed = 'standby'
    q.save()
    return JsonResponse({'type': 'stop', 'source': q.room_number, 'ack_nak': 'ACK'})


# host send 'start' message
# slave change state to the latest query which is in database
# and query_speed should remove
def start_service(request):
    q = BaseInfo.objects.all()[0]
    if q.query_speed != 'None':
        q.current_speed = q.query_speed
        q.query_speed = 'None'
        q.save()
    return JsonResponse({'type': 'send', 'source': q.room_number, 'ack_nak': 'ACK'})


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

