from django.core.management.base import BaseCommand

from cinemanio.core.factories import CastFactory
from cinemanio.core.models import Movie, Person, Cast


class Command(BaseCommand):
    """
    Management command to create test movies, persons and relations
    """

    def flush_db(self):
        for model in [Movie, Person]:
            model.objects.all().delete()

    def handle(self, *args, **options):
        self.flush_db()

        for i in range(1000):
            CastFactory()

        self.stdout.write(self.style.SUCCESS('Successfully seeded {} movies, {} persons, {} cast'.format(
            Movie.objects.count(), Person.objects.count(), Cast.objects.count())))
