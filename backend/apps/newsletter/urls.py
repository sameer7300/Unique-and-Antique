from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.subscribe_newsletter, name='subscribe'),
    path('unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe'),
    path('stats/', views.newsletter_stats, name='stats'),
]
