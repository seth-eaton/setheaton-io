from django.db import models

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
    explicit = models.CharField(default=None, max_length=100)
