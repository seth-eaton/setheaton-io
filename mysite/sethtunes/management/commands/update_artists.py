from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone 
from sethtunes.models import Artist, Album, Song, Embed
from urllib.parse import urljoin, quote
from decouple import config
import applemusicpy
import datetime
import json

class Command(BaseCommand):
    help = 'Updates artist discographies with new releases'

    def handle(self, *args, **options):
        
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
                            if self.release_date(datum['attributes']['releaseDate']) > updated_date:    
                                self.update_album(am, datum, artist)
                        except:
                            self.stdout.write(self.style.NOTICE('Could not access data for album by %s' % artist.artist_name))
                    if len(results['data']) < 25:
                        break
                    else:
                        offset += 25
            except:
                self.stdout.write(self.style.NOTICE('Could not update %s' % artist.artist_name))
            artist.updated_date = timezone.now()
            artist.save(update_fields=['updated_date'])
                
    
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

    def update_album(self, am, datum, artist):
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
                    self.add_song(song_dict, album, artist)
                self.stdout.write(self.style.SUCCESS('Updated %s' % album.album_name))
            except:
                try:
                    album = artist.album_set.create(album_name=album_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, release_date=self.release_date(album_dict['attributes']['releaseDate']), genre=album_dict['attributes']['genreNames'][0], itunes_id=album_dict['id'], artwork_url=album_dict['attributes']['artwork']['url'].format(w=300, h=300), is_single=album_dict['attributes']['isSingle'])
                    song_list = album_dict['relationships']['tracks']['data']
                    for song_dict in song_list:
                        self.add_song(song_dict, album, artist)
                    self.stdout.write(self.style.SUCCESS('Added %s' % datum['attributes']['name']))
                except:
                    self.stdout.write(self.style.NOTICE('Could not add album'))
   

    def add_song(self, song_dict, album, artist):
        try:
            song = album.song_set.create(artist=artist, song_name=song_dict['attributes']['name'], added_date=timezone.now(), artist_name=artist.artist_name, album_name=album.album_name, release_date=self.release_date(song_dict['attributes']['releaseDate']), genre=song_dict['attributes']['genreNames'][0], track_time=datetime.timedelta(milliseconds=song_dict['attributes']['durationInMillis']), itunes_id=song_dict['id'], artwork_url=album.artwork_url)
            try:
                url = song_dict['attributes']['url']
                url = url[url.index('/us'):]
                embed_url = urljoin('https://embed.music.apple.com/', url)
                song.embed_set.create(embed_url=embed_url, embed_type='apple music')
            except:
                self.stdout.write(self.style.NOTICE('Could not get embed link for %s' % song.song_name))
        except:
            self.stdout.write(self.style.NOTICE('Could not add song'))

    def release_date(self, date_str):
        date =  datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_aware = date.replace(tzinfo=datetime.timezone.utc)
        return date_aware
