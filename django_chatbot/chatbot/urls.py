from django.urls import path
from . import views
from .views import submit_signature

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('project_register', views.project_register, name='project_register'),
    path('contract', views.contract, name='contract'),
    path('target/', views.go_to_target, name='go_to_target'),
    path('project/', views.project, name='project'),
    path('submit_signature/', submit_signature, name='submit_signature'),
]