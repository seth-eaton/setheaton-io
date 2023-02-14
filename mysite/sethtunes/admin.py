from django.contrib import admin

from .models import Artist, Album, Song, PFReview, SethReview, Embed

def make_approved(modeladmin, request, queryset):
    queryset.update(seth_app=True)

# Register your models here.
class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['artist_name', 'id']
    actions = [make_approved]

class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'artist_name', 'id']
    actions = [make_approved]
    list_filter = ('seth_app',)

class SongAdmin(admin.ModelAdmin):
    search_fields = ['song_name', 'album_name', 'artist_name', 'id']
    actions = [make_approved]

class PFReviewAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'artist_name']

class SethReviewAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'artist_name']
    autocomplete_fields = ['album']

class EmbedAdmin(admin.ModelAdmin):
    search_fields = ['song_name']

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(PFReview, PFReviewAdmin)
admin.site.register(SethReview, SethReviewAdmin)
admin.site.register(Embed, EmbedAdmin)
