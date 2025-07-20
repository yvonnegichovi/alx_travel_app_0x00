from rest_framework import serializers
from .models import Listing, Booking, Review

class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model.
    Includes host's username for readability.
    """
    host_username = serializers.ReadOnlyField(source='host.username')
    
    class Meta:
        model = Listing
        fields = (
            'listing_id', 'host', 'host_username', 'name', 'description',
            'location', 'price_per_night', 'created_at', 'updated_at'
        )
        read_only_fields = ('listing_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'host': {'write_only': True}
        }

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    Includes guest's username and listing's name for readability.
    """
    guest_username = serializers.ReadOnlyField(source='guest.username')
    listing_name = serializers.ReadOnlyField(source='listing.name')

    class Meta:
        model = Booking
        fields = (
            'booking_id', 'listing', 'listing_name', 'guest', 'guest_username',
            'start_date', 'end_date', 'total_price', 'status', 'created_at'
        )
        read_only_fields = ('booking_id', 'total_price', 'created_at', 'status') 
        extra_kwargs = {
            'listing': {'write_only': True},
            'guest': {'write_only': True}
        }

    def validate(self, data):
        """
        Custom validation for booking dates and total price.
        """
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        

        if 'listing' in data and 'start_date' in data and 'end_date' in data:
            listing = data['listing']
            num_nights = (data['end_date'] - data['start_date']).days
            if num_nights <= 0:
                 raise serializers.ValidationError("Booking must be for at least one night.")
            
            calculated_total_price = listing.price_per_night * num_nights
            if 'total_price' in data and data['total_price'] != calculated_total_price:
                 raise serializers.ValidationError(
                     f"Total price mismatch. Expected {calculated_total_price}, got {data['total_price']}."
                 )
            data['total_price'] = calculated_total_price

        return data

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Includes listing name and guest username for readability.
    """
    listing_name = serializers.ReadOnlyField(source='listing.name')
    guest_username = serializers.ReadOnlyField(source='guest.username')

    class Meta:
        model = Review
        fields = (
            'review_id', 'listing', 'listing_name', 'guest', 'guest_username',
            'rating', 'comment', 'created_at'
        )
        read_only_fields = ('review_id', 'created_at')
        extra_kwargs = {
            'listing': {'write_only': True},
            'guest': {'write_only': True}
        }

    def validate_rating(self, value):
        """
        Validate that rating is between 1 and 5.
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
