from django.urls import path

from .views import *

app_name = "map"
urlpatterns = [
    path('map/', give_map, name='map'),
    path('navigation/', navigation, name='navigation'),
    path('search-path/', search_path, name='search_path_campus'),
    path('log/', log, name='log'),
    path('around/', around, name='around'),
    path('finish/', finish, name='finish'),
]
