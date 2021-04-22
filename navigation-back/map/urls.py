from django.urls import path

from .views import *

app_name = "map"
urlpatterns = [
    path('map/', give_map, name='map'),
    path('navigation/', navigation, name='navigation'),
    path('search-dest/', search_dest, name='search_dest'),
    path('search-path/', search_path, name='search_path'),
    path('search-path-campus/', search_path_campus, name='search_path_campus'),
    path('location/', location, name='location'),
    path('finish/', finish, name='finish'),
    path('log/', log, name='log'),
    path('around/', around, name='around'),
]
