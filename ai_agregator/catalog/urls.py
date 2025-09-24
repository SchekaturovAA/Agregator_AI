from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('toggle_bookmark/<int:service_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks_list'),
    path('service/<int:service_id>/rate/', views.rate_service, name='rate_service'),
]

