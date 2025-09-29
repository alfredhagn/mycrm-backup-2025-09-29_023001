from django.urls import path
from .views_health import healthz
urlpatterns = [ path('healthz', healthz, name='healthz') ]
