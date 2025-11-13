"""
Contact URLs for the Unique and Antique E-commerce Platform.
"""

from django.urls import path
from . import views, admin_views

app_name = 'contact'

urlpatterns = [
    path('messages/', views.ContactMessageCreateView.as_view(), name='create-message'),
    path('messages/list/', views.ContactMessageListView.as_view(), name='list-messages'),
    path('messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='message-detail'),
    path('subjects/', views.contact_subjects, name='contact-subjects'),
    
    # Admin endpoints
    path('admin/contact/stats/', admin_views.AdminContactStatsView.as_view(), name='admin_contact_stats'),
    path('admin/contact/', admin_views.AdminContactListView.as_view(), name='admin_contact_list'),
    path('admin/contact/<int:pk>/', admin_views.AdminContactDetailView.as_view(), name='admin_contact_detail'),
]
