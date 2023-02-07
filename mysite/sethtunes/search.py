from django.db.models import Q, Min
from .models import Artist, Album, Song, PFReview
import random

def search(search_term):
    results = {}
    
    artist_results = Artist.objects.filter(artist_name__icontains=search_term)[:12]
    results.update({'artists':artist_results})

    album_results_name = list(Album.objects.filter(album_name__icontains=search_term).filter(album_type='Album'))
    album_results_artist_raw = list(Album.objects.filter(artist_name__icontains=search_term).filter(album_type='Album').order_by('?'))
    album_results_artist = []
    for artist_result in album_results_artist_raw:
        add = True
        for name_result in album_results_name:
            if artist_result.album_name == name_result.album_name and artist_result.artist_name == name_result.artist_name:
                add = False
        if add:
            album_results_artist.append(artist_result)
    album_results = album_results_name + album_results_artist
    album_results = album_results[:12]
    results.update({'albums':album_results})
    
    song_results_name_raw = list(Song.objects.filter(song_name__icontains=search_term))
    song_results_name = []
    for raw_song in song_results_name_raw:
        add = True
        for clean_song in song_results_name:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        if add:
            song_results_name.append(raw_song)
    song_results_album_raw = list(Song.objects.filter(album_name__icontains=search_term))
    song_results_album = []
    for raw_song in song_results_album_raw:
        add = True
        for clean_song in song_results_album:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        for clean_song in song_results_name:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        if add:
            song_results_album.append(raw_song)
    song_results_artist_raw = list(Song.objects.filter(artist_name__icontains=search_term))
    song_results_artist = []
    for raw_song in song_results_artist_raw:
        add = True
        for clean_song in song_results_artist:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        for clean_song in song_results_name:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        for clean_song in song_results_album:
            if clean_song.artist_name == raw_song.artist_name and clean_song.song_name == raw_song.song_name:
                add = False
        if add:
            song_results_artist.append(raw_song)
    song_results = song_results_artist + song_results_album
    random.shuffle(song_results)
    song_results = song_results_name + song_results
    song_results = song_results[:12]
    results.update({'songs':song_results})
    
    reviews_results = PFReview.objects.filter(Q(album_name__icontains=search_term) | Q(artist_name__icontains=search_term)).order_by('?')[:12]
    results.update({'reviews':reviews_results})
    
    return results
