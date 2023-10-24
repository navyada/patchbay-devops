from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import CommandError

class Command(createsuperuser.Command):
    help = 'Create a superuser with extra fields'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--email', dest='email', required=True, help='Email')
        parser.add_argument('--first_name', dest='first_name', required=True, help='First name')
        parser.add_argument('--last_name', dest='last_name', required=True, help='Last name')
        parser.add_argument('--phone_number', dest='phone_number', required=True, help='Phone number')

    def handle(self, *args, **options):
        email = input['email']
        first_name = input['first_name']
        last_name = input['last_name']
        phone_number = input['phone_number']

        try:
            super(Command, self).handle(*args, **options)
        except CommandError as e:
            self.stderr.write(self.style.ERROR(e))
        else:
            user = self.UserModel.objects.get_or_create(email=email,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        phone_number=phone_number)
            # user.first_name = first_name
            # user.last_name = last_name
            # user.phone_number = phone_number
            user.save()
