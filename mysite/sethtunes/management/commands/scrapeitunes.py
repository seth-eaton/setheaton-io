from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone 
from sethtunes.models import Artist, Album, Song, PFReview
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
import datetime
import requests
import json
import re

class Command(BaseCommand):
    help = 'Scrapes iTunes for data from a list of artists from a file'

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
        
        artist_results = []
        for artist_name in artist_names:
            if (artist_result := self.find_artist(artist_name)):
                artist_results.append(artist_result)
                self.stdout.write(self.style.SUCCESS('Found %s' % artist_name))
            else:
                self.stdout.write(self.style.NOTICE('Could not find %s' % artist_name))

        artists = []
        for artist_result in artist_results:
            try:
                artists.append(self.add_artist(artist_result))
            except:
                self.stdout.write(self.style.NOTICE('Could not add %s' % artist_result['artistName']))

        for artist in artists:
            if (album_results := self.find_albums(artist.itunes_id)):
                self.stdout.write(self.style.SUCCESS('Adding albums for %s' % artist.artist_name))
                for i in range(1, len(album_results)):
                    if (song_results := self.find_songs(album_results[i]['collectionId'])):
                        try:
                            album = self.add_album(artist, album_results[i])
                            try:
                                self.find_pf(album.artist_name, album.album_name, album)
                            except:
                                pass
                            for j in range(1, len(song_results)):
                                if (song := self.add_song(album, artist, song_results[j])):
                                    pass
                        except:
                            self.stdout.write(self.style.NOTICE('Error adding album'))
                    else:
                        self.stdout.write(self.style.NOTICE('Could not find songs for %s' % album_results[i]['collectionName']))
            else:
                self.stdout.write(self.style.NOTICE('Could not find albums for %s' % artist.artist_name))

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

        artist = Artist.objects.all()
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


    def find_artist(self, artist_name):
        spaces_count = artist_name.count(' ')
        search_term = artist_name.replace(' ', '+', spaces_count)
       
        try:
            request = 'https://itunes.apple.com/search?term=' + search_term + '&etnity=song&limit=300'
            response = requests.get(request).json()
            results = response['results']
        except:
            return False

        i = 0
        while i < len(results):
            try:
                if results[i]['artistName'] == artist_name:
                    try:
                        artist_request = 'https://itunes.apple.com/lookup?id=' + str(results[i]['artistId'])
                        artist_response = requests.get(artist_request).json()
                        artist_result = artist_response['results'][0]
                        return artist_result
                    except:
                        return False
                else:
                    i += 1
            except:
                return False
        return False
    
    def add_artist(self, artist_result):
        try:
            a = Artist(artist_name = artist_result['artistName'], added_date = timezone.now(), genre = artist_result['primaryGenreName'], itunes_id = artist_result['artistId'], amg_id = artist_result['amgArtistId'], genre_id = artist_result['primaryGenreId'])
            a.save()
            return a
        except:
            a = Artist(artist_name = artist_result['artistName'], added_date = timezone.now(), genre = artist_result['primaryGenreName'], itunes_id = artist_result['artistId'], amg_id = 0, genre_id = artist_result['primaryGenreId'])
            a.save()
            self.stdout.write(self.style.NOTICE('No amg id for %s' % a.artist_name))
            return a

    def find_albums(self, artist_id):
        request = 'https://itunes.apple.com/lookup?id=' + str(artist_id) + '&entity=album'
        try:
            response = requests.get(request).json()
            return response['results']
        except:
            return False

    def add_album(self, artist, album_result):
        album_type = ''
        if album_result['collectionName'].count('EP') > 0:
            album_type = 'EP'
        elif album_result['collectionName'].count('Single') > 0:
            album_type = 'Single'
        elif album_result['collectionName'].count('Remixes') > 0:
            album_type = 'Remixes'
        else:
            album_type = 'Album'
        album = artist.album_set.create(album_name = album_result['collectionName'], added_date = timezone.now(), artist_name = artist.artist_name, release_date = self.release_date(album_result['releaseDate']), genre = album_result['primaryGenreName'], itunes_id = album_result['collectionId'], artwork_url = album_result['artworkUrl100'], album_type = album_type)
        return album

    def find_songs(self, album_id):
        request = 'https://itunes.apple.com/lookup?id=' + str(album_id) + '&entity=song'
        try:
            response = requests.get(request).json()
            return response['results']
        except:
            return False

    def add_song(self, album, artist, song_result):
        try:
            song = album.song_set.create(artist_id = artist.id, song_name = song_result['trackName'], added_date = timezone.now(), artist_name = artist.artist_name, album_name = album.album_name, release_date = self.release_date(song_result['releaseDate']), genre = song_result['primaryGenreName'], track_time = datetime.timedelta(milliseconds=song_result['trackTimeMillis']), itunes_id = song_result['trackId'], artwork_url = song_result['artworkUrl100'], explicit = song_result['trackExplicitness'])
            return song
        except:
            return False
            self.stdout.write(self.style.NOTICE('Could not find key for %s' % song_result['trackName']))

    def release_date(self, date_str):
        date =  datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        date_aware = date.replace(tzinfo=datetime.timezone.utc)
        return date_aware

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
