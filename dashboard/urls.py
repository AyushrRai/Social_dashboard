from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-post/', views.create_post, name='create_post'),
    path('scheduled-posts/', views.scheduled_posts, name='scheduled_posts'),
    path('analytics/', views.analytics, name='analytics'),
    path('social-accounts/', views.social_accounts, name='social_accounts'),
    path('profile/', views.profile, name='profile'),
]