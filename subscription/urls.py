from django.urls import path
from  . import views
app_name = 'subscription' 
urlpatterns = [
    path("", views.subscription_plans, name="subscription_plans"),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('payment/<int:sub_id>/', views.payment, name='payment'),
    path('success/<int:sub_id>/', views.success, name='success'),
]
