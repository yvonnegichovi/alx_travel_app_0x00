import random
from datetime import timedelta, date
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from faker import Faker
from listings.models import Listing, Booking, Review

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_users',
            type=int,
            default=10,
            help='Number of sample users to create.'
        )
        parser.add_argument(
            '--num_listings',
            type=int,
            default=50,
            help='Number of sample listings to create.'
        )
        parser.add_argument(
            '--num_bookings_per_listing',
            type=int,
            default=5,
            help='Max number of bookings per listing.'
        )
        parser.add_argument(
            '--num_reviews_per_listing',
            type=int,
            default=3,
            help='Max number of reviews per listing.'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before seeding.'
        )

    def handle(self, *args, **options):
        num_users = options['num_users']
        num_listings = options['num_listings']
        num_bookings_per_listing = options['num_bookings_per_listing']
        num_reviews_per_listing = options['num_reviews_per_listing']
        clear_data = options['clear']

        User = get_user_model()

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Seeding database...'))

        with transaction.atomic():
            self.stdout.write(self.style.MIGRATE_HEADING(f'Creating {num_users} users...'))
            users = []
            existing_user_count = User.objects.count()
            if existing_user_count < num_users:
                for i in range(num_users - existing_user_count):
                    user = User.objects.create_user(
                        username=fake.user_name() + str(uuid.uuid4())[:4],
                        email=fake.email(),
                        password='password123',
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=fake.phone_number(),
                        role=random.choice(['guest', 'host'])
                    )
                    users.append(user)
                    self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS('Enough users already exist, skipping user creation.'))
            users = list(User.objects.all())

            if not users:
                raise CommandError("No users available to create listings/bookings. Please create some users or increase --num_users.")

            hosts = [u for u in users if u.role == 'host' or (not hasattr(u, 'role') and not u.is_superuser)]
            guests = [u for u in users if u.role == 'guest' or (not hasattr(u, 'role') and not u.is_superuser)]

            if not hosts:
                self.stdout.write(self.style.WARNING('No host users found. Creating some...'))
                for i in range(max(1, num_users // 5)):
                    host = User.objects.create_user(
                        username=fake.user_name() + '_host_' + str(uuid.uuid4())[:4],
                        email=fake.email(),
                        password='password123',
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=fake.phone_number(),
                        role='host'
                    )
                    hosts.append(host)
                    self.stdout.write(self.style.SUCCESS(f'Created host user: {host.username}'))
                users = list(User.objects.all())
                hosts = [u for u in users if u.role == 'host' or (not hasattr(u, 'role') and not u.is_superuser)] # Re-filter hosts

            if not guests:
                self.stdout.write(self.style.WARNING('No guest users found. Creating some...'))
                for i in range(max(1, num_users // 5)):
                    guest = User.objects.create_user(
                        username=fake.user_name() + '_guest_' + str(uuid.uuid4())[:4],
                        email=fake.email(),
                        password='password123',
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=fake.phone_number(),
                        role='guest'
                    )
                    guests.append(guest)
                    self.stdout.write(self.style.SUCCESS(f'Created guest user: {guest.username}'))
                users = list(User.objects.all())
                guests = [u for u in users if u.role == 'guest' or (not hasattr(u, 'role') and not u.is_superuser)] # Re-filter guests

            self.stdout.write(self.style.MIGRATE_HEADING(f'Creating {num_listings} listings...'))
            listings = []
            for i in range(num_listings):
                host = random.choice(hosts)
                listing = Listing.objects.create(
                    host=host,
                    name=fake.sentence(nb_words=random.randint(3, 7)),
                    description=fake.paragraph(nb_sentences=random.randint(3, 8)),
                    location=fake.city(),
                    price_per_night=random.randint(50, 500) * 100 / 100.0
                )
                listings.append(listing)
                self.stdout.write(self.style.SUCCESS(f'Created listing: "{listing.name}" by {host.username}'))

            if not listings:
                raise CommandError("No listings created. Cannot create bookings or reviews.")

            self.stdout.write(self.style.MIGRATE_HEADING('Creating bookings...'))
            for listing in listings:
                num_bookings = random.randint(0, num_bookings_per_listing)
                for _ in range(num_bookings):
                    guest = random.choice(guests)
                    start_date = fake.date_between(start_date='-1y', end_date='+1y')
                    end_date = start_date + timedelta(days=random.randint(1, 14))
                    
                    num_nights = (end_date - start_date).days
                    total_price = listing.price_per_night * num_nights

                    booking = Booking.objects.create(
                        listing=listing,
                        guest=guest,
                        start_date=start_date,
                        end_date=end_date,
                        total_price=total_price,
                        status=random.choice(['pending', 'confirmed', 'canceled'])
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created booking for {listing.name} by {guest.username}'))

            # 4. Create Reviews
            self.stdout.write(self.style.MIGRATE_HEADING('Creating reviews...'))
            for listing in listings:
                num_reviews = random.randint(0, num_reviews_per_listing)
                for _ in range(num_reviews):
                    guest = random.choice(guests)
                    review = Review.objects.create(
                        listing=listing,
                        guest=guest,
                        rating=random.randint(1, 5),
                        comment=fake.paragraph(nb_sentences=random.randint(1, 3)) if random.random() > 0.3 else None # Optional comment
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created review for {listing.name} by {guest.username}'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
