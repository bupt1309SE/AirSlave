from django.conf.urls import url

from slave import views

app_name = 'slave'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^setting$', views.setting, name='setting'),
    url(r'^host_reply$', views.host_reply, name='host_reply'),
    url(r'^room_reply$', views.room_reply, name='room_reply'),
    url(r'^target_reply$', views.target_reply, name='target_reply'),
    url(r'^speed_reply$', views.speed_reply, name='speed_reply'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^mode_reply', views.mode_reply, name='mode_reply'),
    url(r'^get_info', views.get_info, name='get_info'),
]
