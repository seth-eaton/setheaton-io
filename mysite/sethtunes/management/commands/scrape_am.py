from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone 
from sethtunes.models import Artist, Album, Song, PFReview, Embed, WikiBlurb
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
from decouple import config
import wikipediaapi as wikipedia
import applemusicpy
import datetime
import requests
import json
import re

class Command(BaseCommand):
    help = 'Scrapes apple music for data from a list of artists from a file'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        for filename in options['filename']:
            try:
                with open(filename, 'r') as infile:
                    self.stdout.write(self.style.SUCCESS('opened %s' % filename))
                    artist_names = []
                    for line in infile:
                        try:
                            a = Artist.objects.get(artist_name=line.strip())
                            self.stdout.write(self.style.NOTICE('%s is already in the catalog' % a.artist_name)) 
                        except:
                            artist_names.append(line.strip())
            except:
                raise CommandError('Could not open file %s' % filename)
        
        with open('sethtunes_am_key.p8', 'r') as keyfile:
            am_key=keyfile.read()
        key_id = config("am_key_id")
        team_id = config("am_team_id")
        am = applemusicpy.AppleMusic(am_key, key_id, team_id)

        wiki = wikipedia.Wikipedia('en')

        artist_names = set(artist_names)
        for name in artist_names:
            r = am.search(name, types=['artists'], limit=5)
            try:
                for artist_datum in r['results']['artists']['data']:
                    if artist_datum['attributes']['name'] == name:
                        artist = self.add_artist(artist_datum)
                        self.find_wiki(wiki, artist)
                        self.add_albums(am, artist, artist_datum)
                        break
            except:
                self.stdout.write(self.style.NOTICE('Could not find %s' % name))
                
        for row in Album.objects.all().reverse():
            if Album.objects.filter(album_name=row.album_name).filter(artist_name=row.artist_name).count() > 1:
                self.stdout.write(self.style.NOTICE('Deleting duplicate of %s' % row.album_name))
                row.delete()

        albums = Album.objects.all()
        for album in albums:
            try:
                songs = album.song_set.all()
                if songs:
                    pass
                else:
                    album.delete()
                    self.stdout.write(self.style.NOTICE('No songs for %s, deleting' % album.album_name))
            except:
                self.stdout.write(self.style.NOTICE('Could not retrieve songs for %s' % album.album_name))

        artists = Artist.objects.all()
        for artist in artists:
            try:
                albums = artist.album_set.all()
                if albums:
                    pass
                else:
                    artist.delete()
                    self.stdout.write(self.style.NOTICE('No albums for %s, deleting' % artist.artist_name))
            except:
                self.stdout.write(self.style.NOTICE('Could not retrieve albums for %s' % artist.artist_name))

        self.stdout.write(self.style.SUCCESS('Done!'))

    def add_artist(self, artist_datum):
        try:
            ar = Artist(artist_name=artist_datum['attributes']['name'], added_date=timezone.now(), genre=artist_datum['attributes']['genreNames'][0], itunes_id=artist_datum['id'], artwork_url=artist_datum['attributes']['artwork']['url'].format(w=300, h=300), updated_date=timezone.now()) 
            ar.save()
            self.stdout.write(self.style.SUCCESS('Added %s' % ar.artist_name))
            return ar
        except:
            self.stdout.write(self.style.NOTICE('Could not add %s' % artist_datum['attributes']['name']))
            return None

    def add_albums(self, am, artist, artist_datum):
        try:
            for album_datum in artist_datum['relationships']['albums']['data']:
                album_result=am.album(album_datum['id'], storefront='us', 
                                      l=None, include=None)
                album_dict=album_result['data'][0]
                cleaned=False
                try: 
                    if album_dict['attributes']['contentRating'] == 'clean':
                        cleaned=True
                except:
                    pass

                if not cleaned:
                    try:
                        album = artist.album_set.create(album_name=album_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, release_date=self.release_date(album_dict['attributes']['releaseDate']), genre=album_dict['attributes']['genreNames'][0], itunes_id=album_dict['id'], artwork_url=album_dict['attributes']['artwork']['url'].format(w=300, h=300), is_single=album_dict['attributes']['isSingle'])

                        if not album.is_single:
                            try:
                                self.find_pf(album.artist_name, 
                                             album.album_name, album)
                            except:
                                pass

                        song_list = album_dict['relationships']['tracks']['data']
                        for song_dict in song_list:
                            self.add_song(am, album, artist, song_dict)
                    except:
                        self.stdout.write(self.style.NOTICE('Could not add album'))
        except:
            self.stdout.write(self.style.NOTICE('Could not find albums for %s' % name))
    
    def add_song(self, am, album, artist, song_dict):
        try:
            song = album.song_set.create(artist=artist, song_name=song_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, album_name=album.album_name, release_date=self.release_date(song_dict['attributes']['releaseDate']), genre=song_dict['attributes']['genreNames'][0], track_time=datetime.timedelta(milliseconds=song_dict['attributes']['durationInMillis']), itunes_id=song_dict['id'], artwork_url=album.artwork_url)
            try:
                el = self.get_embed(song_dict['attributes']['url'])
                song.embed_set.create(embed_url=el, embed_type='apple music')
            except:
                self.stdout.write(self.style.NOTICE('Could not get embed link for %s' % so.song_name))
        except:
            self.stdout.write(self.style.NOTICE('Could not add song'))

    def find_wiki(self, wiki, artist):
        try:
            page = wiki.page(artist.artist_name)
            add = False
            if page.exists():
                for category in page.categories:
                    if 'singer' in category.lower() or 'musician' in category.lower() or 'music group' in category.lower() or 'musical group' in category.lower():
                        add = True
            if add:
                artist.wikiblurb_set.create(url=page.fullurl, 
                                            summary=page.summary)
        except:
            pass

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

    def score(self, soup):
        rating = soup.find('p', attrs={'class': re.compile('.*Rating.*')}).text
        return rating.strip()

    def author(self, soup):
        return soup.find('a', attrs={'class': re.compile('.*byline__name-link.*')}).get_text()

    def abstract(self, soup):
        return soup.find('div', attrs={'class': re.compile('.*SplitScreenContentHeaderDekDown.*')}).get_text()

    def editorial(self, soup):
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

    def bnm(self, soup):
        return soup.find('p', attrs={'class': re.compile('.*BestNewMusic.*')}) != None

    def release_date(self, date_str):
        date =  datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_aware = date.replace(tzinfo=datetime.timezone.utc)
        return date_aware

    def get_embed(self, url):
        url = url[url.index('/us'):]
        embed_url = urljoin('https://embed.music.apple.com/', url)
        return embed_url
