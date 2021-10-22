from django.urls import path

from ModeloB.login.views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
]