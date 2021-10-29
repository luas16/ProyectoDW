from django.urls import path
from ModeloB.user.views import *



urlpatterns = [
    path('list/', UserListView.as_view(), name='user_list'),
    path('add/', UserCreateView.as_view(), name='user_create'),
    path('edit/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('change/group/<int:pk>/', UserChangeGroup.as_view(), name='user_change_group'),
    path('perfil/', UserProfileView.as_view(), name='user_profile'),
    path('user/password/', UserChangePasswordView.as_view(), name='user_password'),
  ]