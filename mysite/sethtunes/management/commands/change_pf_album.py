from django.core.management.base import BaseCommand, CommandError
from sethtunes.models import Album, PFReview
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from urllib.request import urlopen, Request
import re

class Command(BaseCommand):
    help = 'Changes PF review for a specific album when given a link'

    def handle(self, *args, **options):
        inp = input('Which albums would you like to get? ')

        try:
            a = Album.objects.get(album_name=inp)
            inp = input('Found %s by %s, would you like to add a new review? (y/n) ' % (a.album_name, a.artist_name))
            if inp == 'y':
                if a.pfreview_set.all().count() > 0:
                    a.pfreview_set.all().delete()
                url = input('Please enter the link: ')
                
                request = Request(url=url, data=None, headers={'User-Agent': 'tejassharma/pitchfork-v0.1'})
                response_text = urlopen(request).read()
                soup = BeautifulSoup(response_text, "lxml")

                try:
                    a.pfreview_set.create(album_name=a.album_name, artist_name=a.artist_name, url=url, score=self.score(soup), author=self.author(soup), abstract=self.abstract(soup), editorial=self.editorial(soup), bnm=self.bnm(soup))
                except:
                    try:
                        a.pfreview_set.create(album_name=a.album_name, artist_name=a.artist_name, url=url, score=self.score(soup), abstract=self.abstract(soup), editorial=self.editorial(soup), bnm=self.bnm(soup))
                    except:
                        try:
                            a.pfreview_set.create(album_name=a.album_name, artist_name=a.artist_name, url=url, score=self.score(soup), editorial=self.editorial(soup), bnm=self.bnm(soup))
                        except:
                            self.stdout.write(self.style.NOTICE('Could not parse the review.'))
            else:
                self.stdout.write(self.style.SUCCESS('k thx cu l8r :)'))
        except:
            self.stdout.write(self.style.NOTICE('There was an error.'))

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
