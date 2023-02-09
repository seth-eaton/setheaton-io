from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.utils import timezone
from .models import Artist, Album, Song, PFReview, Embed
from .search import search
from .sort import sort_albums

# Create your views here.

def index(request):
    album_list = Album.objects.filter(is_single=False).order_by('?')[:400]
    context = {'album_list': album_list}
    return render(request, 'sethtunes/index.html', context)

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, pk=artist_id)
    if artist:
        raw_albums = artist.album_set.filter(is_single=False).order_by('-release_date')
        sorted_albums = sort_albums(raw_albums)
        if len(artist.wikiblurb_set.all()) > 0:
            wikiblurb = artist.wikiblurb_set.all()[0]
            summary = wikiblurb.summary.split('\n')
        else:
            wikiblurb = False
            summary = False
    return render(request, 'sethtunes/artist_detail_test.html', {'artist': artist, 'sorted_albums':sorted_albums, 'wikiblurb':wikiblurb, 'summary':summary})

def album_detail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    view = request.GET.get('view')
    songs = album.song_set.all()
    if len(album.pfreview_set.all()) > 0:
        pfreview = album.pfreview_set.all()[0]
        pfeditorial = pfreview.editorial.split('\n\n')
    else:
        pfreview = False
        pfeditorial = False
    if pfreview and view == "pitchfork":
        pass
    else:
        view = "songs"
    return render(request, 'sethtunes/album_detail.html', {'album':album, 'songs':songs, 'pfreview':pfreview, 'pfeditorial':pfeditorial, 'view':view})

def song_detail(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    try:
        am_embed = song.embed_set.filter(embed_type='apple music').get()
    except:
        am_embed = None
    return render(request, 'sethtunes/song_detail.html', {'song':song, 'am_embed': am_embed})

def search_results(request):
    results = None
    if 'search' in request.POST:
        search_term = request.POST['search']
        results = search(search_term)
    return render(request, 'sethtunes/search_results.html', {'results':results})

def new_music(request):
    albums_raw = Album.objects.filter(release_date__lte=timezone.now()).order_by('-release_date')
    albums = []
    for album_raw in albums_raw[:300]:
        append = True
        for album in albums:
            if album.itunes_id == album_raw.itunes_id:
                append = False
        if append:
            albums.append(album_raw)
    albums = albums[:100]
    return render(request, 'sethtunes/new_music.html', {'albums':albums})

def top_rated(request):
    reviews = PFReview.objects.filter(score__gte=8.5).order_by('-score')
    return render(request, 'sethtunes/top_rated.html', {'reviews':reviews})

def about(request):
    return render(request, 'sethtunes/about.html')
