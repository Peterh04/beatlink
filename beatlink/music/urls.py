from django.urls import path
from . import views

urlpatterns = [
path('',views.index, name='index'),
path('login',views.login, name='login'),
path('logout',views.logout, name='logout'),
path('signup',views.signup, name='signup'),
path('search', views.search, name = 'search' ),
path('music/<str:pk>/', views.music, name='music'),
path('settings/', views.settings, name='settings'),
path('update_credentials/', views.update_credentials, name='update_credentials'),
path('like_song', views.like_song, name='like_song'),
path('liked_songs', views.liked_songs, name='liked_songs'),
path('delete_song/<int:track_id>/', views.delete_song, name='delete_song'),

]
