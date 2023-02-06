from django.core.management.base import BaseCommand, CommandError
from sethtunes.models import Artist, Album, Song, PFReview, Embed

class Command(BaseCommand):
    help = 'Removed duplicate albums based on explicitness'

    def handle(self, *args, **options):
        for row in Album.objects.all().reverse():
            if Album.objects.filter(album_name=row.album_name).count() > 1:
                row.delete()
