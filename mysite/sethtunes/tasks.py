from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from django.utils import timezone
from sethtunes.models import Artist, Album, Song, Embed, PFReview, WikiBlurb
from urllib.parse import urljoin, quote
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
from decouple import config
import wikipediaapi as wikipedia
import applemusicpy
import datetime
import json
import re

@shared_task(name = "get_latest_pf_sethtunes")
def get_latest():

    with open('sethtunes_am_key.p8', 'r') as keyfile:
        am_key = keyfile.read()
    key_id = config("am_key_id")
    team_id = config("am_team_id")
    am = applemusicpy.AppleMusic(am_key, key_id, team_id)

    wiki = wikipedia.Wikipedia('en')

    request = Request(url='https://pitchfork.com/reviews/albums/',
                      data=None,
                      headers={'User-Agent': 'tegassharma/pitchfork-v0.1'})
    response = urlopen(request)
    text = response.read().decode('UTF-8').split('window.App=')[1].split(';</script>')[0]

    obj = json.loads(text)

    reviews = obj['context']['dispatcher']['stores']['ReviewsStore']['items']

    for review in reviews:
        review_artist = reviews[review]['artists'][0]['display_name']
        review_album = reviews[review]['tombstone']['albums'][0]['album']['display_name']
        score = reviews[review]['tombstone']['albums'][0]['rating']['rating']
        try:
            album = Album.objects.filter(artist_name=review_artist).filter(album_name=review_album).get()
            if album.pfreview_set.count() == 0:
                add_review(album, reviews[review]['url'])
        except:
            if float(score) >= 5:
                try:
                    artist = Artist.objects.filter(artist_name=review_artist).get()
                except:
                    try:
                        add_artist_am(am, wiki, review_artist)
                    except:
                        pass

    for row in Album.objects.all().reverse():
        if Album.objects.filter(album_name=row.album_name).filter(artist_name=row.artist_name).count() > 1:
            print('Deleting duplicate of %s' % row.album_name)
            row.delete()

    albums = Album.objects.all()
    for album in albums:
        try:
            songs = album.song_set.all()
            if songs:
                pass
            else:
                album.delete()
                print('No songs for %s, deleting' % album.album_name)
        except:
            print('Could not retrieve songs for %s' % album.album_name)

    artists = Artist.objects.all()
    for artist in artists:
        albums = artist.album_set.all()
        if albums:
            pass
        else:
            artist.delete()
            print('No albums for %s, deleting' % artist.artist_name)

    print('Done!')

@shared_task(name = "update_artist_main")
def update_artist():

    with open('sethtunes_am_key.p8', 'r') as keyfile:
        am_key=keyfile.read()
    key_id = config("am_key_id")
    team_id = config("am_team_id")
    am = applemusicpy.AppleMusic(am_key, key_id, team_id)

    artists = Artist.objects.all()
    for artist in artists:
        updated_date = artist.updated_date
        offset = 0
        try:
            while results := am.artist_relationship(artist.itunes_id,
                                                    'albums',
                                                    offset=offset):
                for datum in results['data']:
                    try:
                        if release_date(datum['attributes']['releaseDate']) > updated_date:
                            update_album(am, datum, artist)
                    except:
                        pass
                if len(results['data']) < 25:
                    break
                else:
                    offset += 25
        except:
            pass
        artist.updated_date = timezone.now()
        artist.save()

    for row in Album.objects.all().reverse():
        if Album.objects.filter(album_name=row.album_name).filter(artist_name=row.artist_name).count() > 1:
            print('Deleting duplicate of %s' % row.album_name)
            row.delete()

    albums = Album.objects.all()
    for album in albums:
        try:
            songs = album.song_set.all()
            if songs:
                pass
            else:
                album.delete()
                print('No songs for %s, deleting' % album.album_name)
        except:
            print('Could not retrieve songs for %s' % album.album_name)

    artists = Artist.objects.all()
    for artist in artists:
        albums = artist.album_set.all()
        if albums:
            pass
        else:
            artist.delete()
            print('No albums for %s, deleting' % artist.artist_name)

    print('Done!')

def update_album(am, datum, artist):
    album_data = am.album(datum['id'], storefront='us', l=None, include=None)
    album_dict = album_data['data'][0]

    cleaned=False
    try:
        if album_dict['attributees']['contentRating'] == 'clean':
            cleaned=True
    except:
        pass

    if not cleaned:
        try:
            album = Album.objects.filter(album_name=album_dict['attributes']['name']).get()
            album.song_set.all().delete()
            song_list = album_dict['relationships']['tracks']['data']
            for song_dict in song_list:
                add_song(song_dict, album, artist)
            print('Updated %s' % album.album_name)
        except:
            try:
                album = artist.album_set.create(album_name=album_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, release_date=release_date(album_dict['attributes']['releaseDate']), genre=album_dict['attributes']['genreNames'][0], itunes_id=album_dict['id'], artwork_url=album_dict['attributes']['artwork']['url'].format(w=300, h=300), is_single=album_dict['attributes']['isSingle'])
                song_list = album_dict['relationships']['tracks']['data']
                for song_dict in song_list:
                    add_song(song_dict, album, artist)
                print('Added %s' % datum['attributes']['name'])
            except:
                print('Could not add album')

def add_song(song_dict, album, artist):
    try:
        song = album.song_set.create(artist=artist, song_name=song_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, album_name=album.album_name, release_date=release_date(song_dict['attributes']['releaseDate']), genre=song_dict['attributes']['genreNames'][0], track_time=datetime.timedelta(milliseconds=song_dict['attributes']['durationInMillis']), itunes_id=song_dict['id'], artwork_url=album.artwork_url)
        try:
            url = song_dict['attributes']['url']
            url = url[url.index('/us'):]
            embed_url = urljoin('https://embed.music.apple.com/', url)
            song.embed_set.create(embed_url=embed_url, embed_type='apple music')
        except:
            print('Could not get embed link for %s' % song.song_name)
    except:
        pass

def release_date(date_str):
    date =  datetime.datetime.strptime(date_str, '%Y-%m-%d')
    date_aware = date.replace(tzinfo=datetime.timezone.utc)
    return date_aware

def add_review(album, url):
    full_url = urljoin('http://pitchfork.com/', url)
    request = Request(url=full_url,
                      data=None,
                      headers={'User-Agent': 'tejassharma/pitchfork-v0.1'})
    response_text = urlopen(request).read()
    soup = BeautifulSoup(response_text, "lxml")

    if soup.find(class_='review-multi') is None:
        try:
            r = PFReview(album=album, album_name=album.album_name, artist_name=album.artist_name, url=url, score=score(soup), author=author(soup), abstract=abstract(soup), editorial=editorial(soup), bnm=bnm(soup))
            r.save()
            print('Added PF review for %s' % album.album_name)
        except:
            print('Could not add PF review for %s' % album.album_name)
    else:
        print('Found multi review for %s' % album.album_name)

def score(soup):
    rating = soup.find('p', attrs={'class': re.compile('.*Rating.*')}).text
    return rating.strip()

def author(soup):
    return soup.find('a', attrs={'class': re.compile('.*byline__name-link.*')}).get_text()

def abstract(soup):
    return soup.find('div', attrs={'class': re.compile('.*SplitScreenContentHeaderDekDown.*')}).get_text()

def editorial(soup):
    editorials = soup.find_all(class_='body__inner-container')
    text = ''
    for editorial in editorials:
        for el in editorial:
            if el.name == 'p':
                text += el.text + '\n\n'
            elif el.name == 'hr':
                return text
            else:
                pass
    return text

def bnm(soup):
    return soup.find('p', attrs={'class': re.compile('.*BestNewMusic.*')}) != None

def add_artist_am(am, wiki, artist_name):
    r = am.search(artist_name, types=['artists'], limit=5)
    artist = False
    for artist_datum in r['results']['artists']['data']:
        if artist_datum['attributes']['name'] == artist_name:
            artist = Artist(artist_name=artist_name, added_date=timezone.now(),
                            genre=artist_datum['attributes']['genreNames'][0],
                            itunes_id=artist_datum['id'],
                            artwork_url=artist_datum['attributes']['artwork']['url'].format(w=300, h=300),
                            updated_date=timezone.now())
            artist.save()
            print('Added %s' % artist.artist_name)
            break

    if artist:
        try:
            add_wiki(wiki, artist)
            offset = 0
            while results := am.artist_relationship(artist.itunes_id,
                                                    'albums',
                                                    offset=offset):
                for datum in results['data']:
                    try:
                        add_album(am, datum, artist)
                    except:
                        pass
                if len(results['data']) < 25:
                    break
                else:
                    offset += 25
        except:
            pass

def add_album(am, album_datum, artist):
    r = am.album(album_datum['id'], storefront='us', l=None, include=None)
    album_dict = r['data'][0]
    cleaned=False
    try:
        if album_dict['attributes']['contentRating'] == 'clean':
            cleaned=True
    except:
        pass

    if not cleaned:
        try:
            album = artist.album_set.create(album_name=album_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, release_date=release_date(album_dict['attributes']['releaseDate']), genre=album_dict['attributes']['genreNames'][0], itunes_id=album_dict['id'], artwork_url=album_dict['attributes']['artwork']['url'].format(w=300, h=300), is_single=album_dict['attributes']['isSingle'])
            if not album.is_single:
                try:
                    find_pf(album.artist_name, album.album_name, album)
                except:
                    pass
            song_list=album_dict['relationships']['tracks']['data']
            for song_dict in song_list:
                try:
                    add_song(song_dict, album, artist)
                except:
                    pass
        except:
            pass

def find_pf(artist_name, album_name, album):
    query = '{} {}'.format(artist_name, album_name)
    query = quote(query)
    # using a custom user agent header
    request = Request(url='http://pitchfork.com/search/?query=' + query,
                      data=None,
                      headers={'User-Agent': 'tejassharma/pitchfork-v0.1'})
    response = urlopen(request)
    text = response.read().decode('UTF-8').split('window.App=')[1].split(';</script>')[0]

    # the server responds with json so we load it into a dictionary
    obj = json.loads(text)

    try:
        # get the nested dictionary containing url to the review and album name
        review_dict = obj['context']['dispatcher']['stores']['SearchStore']['results']['albumreviews']['items'][0]

        url = review_dict['url']
        matched_artist = review_dict['artists'][0]['display_name']

        #print(json.dumps(review_dict, indent=2))

        # fetch the review page
        full_url = urljoin('http://pitchfork.com/', url)
        request = Request(url=full_url,
                          data=None,
                          headers={'User-Agent': 'tejassharma/pitchfork-v0.1'})
        response_text = urlopen(request).read()
        soup = BeautifulSoup(response_text, "lxml")

        if soup.find(class_='review-multi') is None:
            r = PFReview(album=album, album_name=album_name, artist_name=artist_name, url=url, score=score(soup), author=author(soup), abstract=abstract(soup), editorial=editorial(soup), bnm=bnm(soup))
            r.save()
            print('Found PF review for %s' % album_name)
        else:
            pass
    except IndexError:
        pass

def add_wiki(wiki, artist):
    try:
        page = wiki.page(artist.artist_name)
        add = False
        if page.exists():
            for category in page.categories:
                if 'singer' in category.lower() or 'musician' in category.lower() or 'music group' in category.lower() or 'musical group' in category.lower():
                    add = True
        if add:
            artist.wikiblurb_set.create(url=page.fullurl, summary=page.summary)
    except:
        pass
