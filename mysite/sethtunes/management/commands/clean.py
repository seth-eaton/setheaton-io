from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone 
from sethtunes.models import Artist, Album, Song, PFReview, Embed
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
from decouple import config
import applemusicpy
import datetime
import requests
import json
import re

class Command(BaseCommand):
    help = 'Scrapes iTunes for data from a list of artists from a file'

    def handle(self, *args, **options):
        for album in Album.objects.all():
            if album.song_set.filter(explicit='explicit').count() > 0:
                album.explicit='explicit'
                album.save()
            elif album.song_set.filter(explicit='cleaned').count() > 0:
                album.explicit='cleaned'
                album.save()
                self.stdout.write(self.style.NOTICE('Found clean version of %s' % album.album_name))
            else:
                album.explicit='notExplicit'
                album.save()
        Album.objects.all().filter(explicit='cleaned').delete()

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
