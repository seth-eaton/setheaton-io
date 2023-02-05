from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
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
        singles_query = Q(album_type='Single')
        singles_query.add(Q(album_type='Remixes'), Q.OR)
        singles = artist.album_set.filter(singles_query).order_by('-release_date').values()
    return render(request, 'sethtunes/artist_detail_test.html', {'artist': artist, 'albums':albums, 'eps':eps, 'singles':singles})

def album_detail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    songs = album.song_set.all()
    if len(album.pfreview_set.all()) > 0:
        pfreview = album.pfreview_set.all()[0]
        pfeditorial = pfreview.editorial.split('\n\n')
    else:
        pfreview = False
        pfeditorial = False
    return render(request, 'sethtunes/album_detail.html', {'album':album, 'songs':songs, 'pfreview':pfreview, 'pfeditorial':pfeditorial})

def song_detail(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    try:
        am_embed = song.embed_set.filter(embed_type='apple music').get()
    except:
        am_embed = None
    return render(request, 'sethtunes/song_detail.html', {'song':song, 'am_embed': am_embed})
