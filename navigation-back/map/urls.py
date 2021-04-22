from django.urls import path

from .views import *

app_name = "map"
urlpatterns = [
    path('map/', map, name='map'),
    path('navigation/', navigation, name='navigation'),
    path('search-dest/', search_dest, name='search_dest'),
    path('search-path/', search_path, name='search_path'),
    path('location/', location, name='location'),
    path('finish/', finish, name='finish'),
    path('log/', log, name='log'),
    path('around/', around, name='around'),
]
