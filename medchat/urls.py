from django.urls import path 
app_name='medchat'

from . import views 

urlpatterns=[
    path('',views.index,name='chat-index'),
    path('<str:room_name>/',views.room_view,name='chat-room'),
]