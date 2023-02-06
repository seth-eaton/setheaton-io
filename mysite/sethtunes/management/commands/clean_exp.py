from django.core.management.base import BaseCommand, CommandError
from sethtunes.models import Artist, Album, Song, PFReview, Embed

class Command(BaseCommand):
    help = 'Removed duplicate albums based on explicitness'

    def handle(self, *args, **options):
        for album in Album.objects.all():
            if album.song_set.filter(explicit='explicit').count() > 0:
                album.explicit='explicit'
                album.save()
            elif album.song_set.filter(explicit='cleaned').count() > 0:
                album.explicit='cleaned'
                album.save()
            else:
                album.explicit='notExplicit'
                album.save()
        Album.objects.all().filter(explicit='cleaned').delete()
