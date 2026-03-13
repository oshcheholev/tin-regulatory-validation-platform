from django.core.management.base import BaseCommand
from apps.rule_extraction.pipeline import seed_default_rules


class Command(BaseCommand):
    help = 'Seed database with default TIN validation rules for common countries'

    def handle(self, *args, **options):
        self.stdout.write('Seeding default TIN rules...')
        seed_default_rules()
        self.stdout.write(self.style.SUCCESS('Default TIN rules seeded successfully!'))
