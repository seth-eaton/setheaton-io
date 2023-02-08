from django.core.management.base import BaseCommand, CommandError
from sethtunes.models import Artist
import wikipediaapi as wikipedia
import requests
import json

class Command(BaseCommand):
    help = 'Scrapes iTunes for data from a list of artists from a file'

    def handle(self, *args, **options):
        wiki = wikipedia.Wikipedia('en')

        for artist in Artist.objects.all():
            page = wiki.page(artist.artist_name)
            add = False
            if page.exists():
                for category in page.categories:
                    if 'singer' in category.lower() or 'musician' in category.lower() or 'music group' in category.lower() or 'musical group' in category.lower():
                        add = True
            if add:
                artist.wikiblurb_set.create(url=page.fullurl, summary=page.summary)
                self.stdout.write(self.style.SUCCESS('Found wiki for %s' % artist.artist_name))
            else:
                self.stdout.write(self.style.NOTICE('Could not find wiki for %s' % artist.artist_name))
