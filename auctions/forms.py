from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "category", "img"]

# TODO: Discard? Currently unused
class BidForm(forms.Form):
    amount = forms.DecimalField(
        label="Place a Bid ",
        max_digits=12,
        decimal_places=2
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]