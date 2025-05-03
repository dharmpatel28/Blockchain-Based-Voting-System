from django.urls import path

from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin', views.admin_login, name='admin'),
    path('user', views.user, name='user'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('start_election', views.start_election, name='start_election'),
    path('end_election', views.end_election, name='end_election'),
    path('add_candidate', views.add_candidate, name='add_candidate'),
    path('register-voter', views.register_voter, name='register_voter'),
    path('result', views.show_results, name='show_results'),
]