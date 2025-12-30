"""
Management command to pre-generate recommendations for all users.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.recommendations.engine import get_recommendation_engine


class Command(BaseCommand):
    help = 'Generate recommendations for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Generate recommendations for a specific user (username)',
        )

    def handle(self, *args, **options):
        engine = get_recommendation_engine()

        # Always keep `users` as a QuerySet (NOT a list)
        if options.get('user'):
            users = User.objects.filter(username=options['user'], is_active=True)

            if not users.exists():
                self.stdout.write(
                    self.style.ERROR(f'User not found: {options["user"]}')
                )
                return
        else:
            users = User.objects.filter(is_active=True)

        user_count = users.count()
        self.stdout.write(
            f'Generating recommendations for {user_count} user(s)...'
        )

        for user in users:
            try:
                recommendations = engine.get_recommendations(user, limit=10)
                self.stdout.write(
                    f'  {user.username}: {len(recommendations)} recommendations'
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Error for {user.username}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully generated recommendations!')
        )
