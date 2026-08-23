from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.member_list_view, name='member_list'),
    path('members/search/', views.search_members_view, name='search_members'),
    path('members/<int:pk>/', views.member_detail_view, name='member_detail'),
    path('members/<int:pk>/edit/', views.edit_member_view, name='edit_member'),
    path('members/<int:pk>/toggle-status/', views.toggle_member_status_view, name='toggle_member_status'),
]
