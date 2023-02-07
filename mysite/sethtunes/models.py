from django.db import models

from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
import re

# Create your models here.

class Artist(models.Model):
    artist_name = models.CharField(max_length=500)
    added_date = models.DateTimeField('date added')
    genre = models.CharField(max_length=100)
    itunes_id = models.IntegerField(default=0)
    amg_id = models.IntegerField(default=0)
    genre_id = models.IntegerField(default=0)

class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=1000)
    added_date = models.DateTimeField('date added')
    artist_name = models.CharField(max_length=500)
    release_date = models.DateTimeField('date released')
    genre = models.CharField(max_length=100)
    itunes_id = models.IntegerField(default=0)
    artwork_url = models.CharField(default=None, max_length=300)
    album_type = models.CharField(default='Album', max_length=100)
    explicit = models.CharField(null=True, blank=True, max_length=100)

class Song(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song_name = models.CharField(max_length=1000)
    added_date = models.DateTimeField('date added')
    artist_name = models.CharField(max_length=500)
    album_name = models.CharField(max_length=1000)
    release_date = models.DateTimeField('date released')
    genre = models.CharField(max_length=100)
    track_time = models.CharField(default=None, max_length=40)
    itunes_id = models.IntegerField(default=0)
    artwork_url = models.CharField(default=None, max_length=300)
    explicit = models.CharField(null=True, blank=True, max_length=100)

class PFReview(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=1000)
    artist_name = models.CharField(max_length=500)
    url = models.CharField(max_length=200)
    score = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    author = models.CharField(default=None, max_length=500)
    abstract = models.CharField(default=None, max_length=1500)
    editorial = models.CharField(default=None, max_length = 25000)
    bnm = models.BooleanField(default=False)

    def __str__(self):
        return self.artist_name + ': ' + self.album_name

class Embed(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    embed_url = models.CharField(max_length=300)
    embed_type = models.CharField(max_length=100)

