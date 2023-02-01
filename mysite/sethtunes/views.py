from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Artist, Album, Song
import random

youtube_auth_key = 'AIzaSyD3772rMfXjWFi0EUdYtUEcj_0mI8vNEOk'

# Create your views here.

def index(request):
    album_list = Album.objects.filter(album_type='Album').order_by('?')[:400]
    context = {'album_list': album_list}
    return render(request, 'sethtunes/index.html', context)

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, pk=artist_id)
    if artist:
        albums = artist.album_set.filter(album_type='Album').order_by('-release_date').values()
        eps = artist.album_set.filter(album_type='EP').order_by('-release_date').values()
        singles = artist.album_set.filter(album_type='Single').order_by('-release_date').values()
    return render(request, 'sethtunes/artist_detail_test.html', {'artist': artist, 'albums':albums, 'eps':eps, 'singles':singles})

def album_detail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    songs = album.song_set.all()
    return render(request, 'sethtunes/album_detail.html', {'album':album, 'songs':songs})

def song_detail(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    return render(request, 'sethtunes/song_detail.html', {'song':song})

def embed_test(request):
    return render(request, 'sethtunes/embed_test.html')
