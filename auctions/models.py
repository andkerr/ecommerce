from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils import timezone

class User(AbstractUser):
    """
    Django's `AbstractUser` class (unlike model classes that 
    extend models.Model) has built-in functionality
    for site user attributes. The relevant ones here
    are username and password.
    """
    pass

class Listing(models.Model):
    """
    Each listing object contains the following attributes:
        - id (primary key, auto-generated)
        - title
        - description
        - starting_price
        - current_price
        - category (optional)
        - image (optional)
        - created by
        - currently active (defaults to True)
        - publication date
    """
    def current_price(self):
        return Bid.objects.filter(listing=self).order_by("-pub_date")[0].amount

    title = models.CharField(max_length=64)
    description = models.TextField(
        help_text="200 characters max.",
        max_length=200
    )

    starting_bid = models.DecimalField(
        "Starting Bid $",
        max_digits=12,
        decimal_places=2,
        default=0
    )
    price = models.DecimalField(
        "Price $",
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Listing class category choices are defined as constants before including
    # them in field optional args, per Django best practice.
    FASHION = 'fashion'
    TOYS = 'toys'
    ELECTRONICS = 'electronics'
    HOME = 'home'
    SPORTS = 'sports'
    OTHER = 'other'
    CATEGORY_CHOICES = [
        (FASHION, 'Fashion'),
        (TOYS, 'Toys'),
        (ELECTRONICS, 'Electronics'),
        (HOME, 'Home'),
        (SPORTS, 'Sports'),
        (OTHER, 'Other')
    ]
    category = models.CharField(
        "Category (optional)",
        max_length=11,
        choices=CATEGORY_CHOICES,
        blank = True
    )

    img = models.ImageField(
        "Upload an Image (optional)",
        upload_to='auctions',
        blank=True,
        null=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="published_listings")
    pub_date = models.DateTimeField("Date Published", default=timezone.now)
    currently_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    """
    The Bid class links bids (time and amount) to the user who placed
    the bid, and the listing on which the bid was placed.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    pub_date = models.DateTimeField("Bid Date", default=timezone.now)

    def __str__(self):
        return f"{self.listing}: ${self.amount}"

class Comment(models.Model):
    """
    The Comment class links comment (time and text) to the user who posted
    the comment, and the listing on which the comment was made.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(help_text="200 characters max.", max_length=200)
    pub_date = models.DateTimeField("Comment Date", default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}: \"{self.text}\""

class Watchlist(models.Model):
    """
    A many-to-many table that links users and listings via user.id
    and listing.id keys.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}, {self.listing}"
