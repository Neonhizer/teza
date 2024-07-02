# from django.urls import path
# from . import views

# urlpatterns = [
#     path('harta', views.harta, name='harta'), 
#     path('street', views.streetview, name='street'),
#     path('aula', views.scrape_bizbrasov, name='aula'),
#     path('get_images/', views.get_images, name='get_images'),

# ]


from django.urls import path
from . import views

urlpatterns = [
   path('harta', views.harta, name='harta'),
    path('get_images_centru_civic/', views.get_images_centru_civic, name='get_images_centru_civic'),
    path('get_images_centru_vechi/', views.get_images_centru_vechi, name='get_images_centru_vechi'),
    path('aula/', views.aula, name='aula'),
    
    path('street/', views.streetview, name ='street' ),
    path('get_all_events/', views.get_all_events, name='get_all_events'),
    path('primaria/',views.primaria, name ='primaria'),
    path('events_aula/', views.events_aula, name='events_aula'),
    path('events_primaria/', views.events_primaria, name='events_primaria'),

    path('events_teatru/', views.events_teatru, name='events_primaria'),
     path('events_filme/', views.events_filme, name='events_primaria'),

     
    path('teatru/', views.teatru, name='teatru'),
    path('chat_with_mistral/', views.chat_with_mistral, name='chat_with_mistral'),
    path('cinema_city/', views.cinema_city, name = 'cinema_city'),
    path('clear-chat-history/', views.clear_chat_history, name='clear_chat_history'),
    path('data_aula/', views.data_aula, name='data_aula'),

    path('events_by_date_aula/', views.events_by_date_aula, name='events_by_date_aula'),


    path('data_teatru/', views.data_teatru, name='data_teatru'),
    path('events_by_date_teatru/', views.events_by_date_teatru, name='events_by_date_teatru'),



   
    
]



