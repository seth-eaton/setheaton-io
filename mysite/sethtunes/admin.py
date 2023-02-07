from django.contrib import admin

from .models import Artist, Album, Song, PFReview, Embed

# Register your models here.
class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['artist_name', 'id']

class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'artist_name', 'id']

class SongAdmin(admin.ModelAdmin):
    search_fields = ['song_name', 'album_name', 'artist_name', 'id']

class PFReviewAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'artist_name']

class EmbedAdmin(admin.ModelAdmin):
    search_fields = ['song_name']

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(PFReview, PFReviewAdmin)
admin.site.register(Embed)
