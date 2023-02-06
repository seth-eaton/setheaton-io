from django.db.models import Q, Min
from .models import Artist, Album, Song, PFReview

def search(search_term):
    results = {}
    artist_results = Artist.objects.filter(artist_name__icontains=search_term)[:10]
    results.update({'artists':artist_results})
    album_results = Album.objects.filter(album_name__icontains=search_term).filter(album_type='Album')
    results.update({'albums':album_results})
    song_results = Song.objects.filter(song_name__icontains=search_term)[:10]
    results.update({'songs':song_results})
    reviews_results = PFReview.objects.filter(Q(album_name__icontains=search_term) | Q(artist_name__icontains=search_term))[:10]
    results.update({'reviews':reviews_results})
    return results
