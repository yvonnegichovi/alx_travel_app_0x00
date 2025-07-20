import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Listing(models.Model):
    """
    Model representing a property listing.
    Corresponds to 'Property' in the database specification.
    """
    listing_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique UUID for the listing"
    )

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        help_text="The user who hosts this listing"
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the listing"
    )
    description = models.TextField(
        help_text="Detailed description of the listing"
    )
    location = models.CharField(
        max_length=255,
        help_text="Geographical location of the listing"
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night for the listing"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Timestamp when the listing was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the listing was last updated"
    )

    class Meta:
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.location}) by {self.host.username}"

class Booking(models.Model):
    """
    Model representing a booking for a listing.
    """
    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique UUID for the booking"
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="The listing that is booked"
    )

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_made',
        help_text="The user who made the booking"
    )
    start_date = models.DateField(
        help_text="Start date of the booking"
    )
    end_date = models.DateField(
        help_text="End date of the booking"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total price for the booking"
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the booking"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Timestamp when the booking was created"
    )

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-created_at']
 
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'guest', 'start_date', 'end_date'],
                name='unique_booking_per_listing_guest_date'
            )
        ]

    def __str__(self):
        return f"Booking {self.booking_id} for {self.listing.name} by {self.guest.username}"

class Review(models.Model):
    """
    Model representing a review for a listing.
    """
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique UUID for the review"
    )

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The listing being reviewed"
    )

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_written',
        help_text="The user who wrote the review"
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating given to the listing (1-5)"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Optional comment for the review"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Timestamp when the review was created"
    )

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.review_id} for {self.listing.name} by {self.guest.username} - Rating: {self.rating}"
