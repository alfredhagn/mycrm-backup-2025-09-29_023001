from django.urls import path
from django.shortcuts import redirect
from .views_planner import  plan_today, plan_save

urlpatterns = [
    path('plan/links/', lambda r: redirect('/crm/plan/today/'), name='plan_links'),
    path('plan/today/', plan_today, name='plan_today'),
    path('plan/save/',  plan_save,  name='plan_save'),
    path('plan/links/', lambda r: redirect('/crm/plan/today/'), name='redirect_to_today'),
]
