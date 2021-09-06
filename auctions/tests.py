from django.test import TestCase
from django.urls import reverse

from .models import Listing

# Create your tests here.
class ListingModelTests(TestCase):
    def test_new_listing_is_currently_active(self):
        """
        Newly created listings are currently active by default.
        """
        new_listing = Listing()
        self.assertIs(new_listing.currently_active, True)

class IndexViewTests(TestCase):
    def test_no_listings(self):
        """
        If no listings exist, none are displayed on the index page.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["listings"], [])

    def test_display_listings(self):
        """
        Index view displays all created listings.
        """
        listing = Listing.objects.create()
        response = self.client.get(reverse('index'))
        self.assertQuerysetEqual(response.context["listings"], [listing])
        