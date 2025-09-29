from django.urls import path
from .views_tiles import tiles
urlpatterns = [ path('tiles/', tiles, name='tiles') ]
