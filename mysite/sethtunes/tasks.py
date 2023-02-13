from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime

from django.utils import timezone
from sethtunes.models import Artist, Album, Song, Embed, PFReview
from urllib.parse import urljoin, quote
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
from decouple import config
import applemusicpy
import datetime
import json
import re

@shared_task(name = "get_latest_pf_sethtunes")
def get_latest():
    
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
        
        try:
            album = Album.objects.filter(artist_name=review_artist).filter(album_name=review_album).get()
            if album.pfreview_set.count() == 0:
                add_review(album, reviews[review]['url'])
        except:
            pass

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

def find_pf(self, artist_name, album_name, album):
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
            r = PFReview(album=album, album_name=album_name, artist_name=artist_name, url=url, score=self.score(soup), author=self.author(soup), abstract=self.abstract(soup), editorial=self.editorial(soup), bnm=self.bnm(soup))
            r.save()
            self.stdout.write(self.style.SUCCESS('Found PF review for %s' % album_name))
        else:
            pass
    except IndexError:
        pass

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
