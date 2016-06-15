from django import forms


class HostForm(forms.Form):
    ip_address = forms.GenericIPAddressField(label='ip地址')
    port_address = forms.IntegerField(label='端口', min_value=0, max_value=65535)


class RoomNumberForm(forms.Form):
    room_number = forms.IntegerField(label='房间号', min_value=1, max_value=10)


class TargetTempForm(forms.Form):
    target_temp = forms.IntegerField(label='目标温度',min_value=18,max_value=30)


class SpeedForm(forms.Form):
    SPEED_CHOICE = (
        ('low', '低速风'),
        ('medium', '中速风'),
        ('high', '高速风'),
        ('standby', '待机')
    )
    speed_choice = forms.ChoiceField(choices=SPEED_CHOICE, label='风速选择')
