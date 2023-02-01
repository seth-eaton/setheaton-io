from django.urls import path
from . import views

app_name = 'sethtunes'
urlpatterns = [
    path('', views.index, name='index'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('song/<int:song_id>/', views.song_detail, name='song_detail'),
    path('embed_test', views.embed_test, name='embed_test'),
]
