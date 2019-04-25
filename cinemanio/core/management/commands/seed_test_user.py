from django.core.management.base import BaseCommand

from cinemanio.users.factories import UserFactory
from cinemanio.users.models import User


class Command(BaseCommand):
    """
    Management command to recreate test user
    """

    def handle(self, *args, **options):
        User.objects.all().delete()

        # create test user
        user = UserFactory(username='testuser', email='testuser@gmail.com')
        user.set_password('t_e_s_t_u_s_e_r')
        user.save()

        self.stdout.write(self.style.SUCCESS('Successfully recreated test user'))
