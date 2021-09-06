from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(currently_active=True).order_by("-pub_date")
    return render(request, "auctions/index.html", {
        "header": "Active Listings",
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If login access is part of a redirect to another view
            # (e.g. watchlist_add), redirect user to that view once
            # they are logged in.
            if request.POST.get("next", False):
                return HttpResponseRedirect(request.POST["next"])
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html", {
            "next": request.GET.get("next", False)
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        if float(request.POST["starting_bid"]) == 0:
            form = ListingForm(request.POST, request.FILES)
            return render(request, "auctions/create.html", {
                "form": form,
                "error_message": "Starting bids must be greater than $0."
            })
        else:
            new_listing = Listing(
                title=request.POST["title"],
                description=request.POST["description"],
                starting_bid=float(request.POST["starting_bid"]),
                category=request.POST["category"],
                img=request.FILES["img"],
                creator=request.user,
                pub_date=timezone.now()
            )
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm()
        categories = [t[1] for t in Listing().CATEGORY_CHOICES]
        return render(request, "auctions/create.html", {
            "form": form,
            "categories": categories
        })

def listing(request, listing_id, error_message=None):
    listing = Listing.objects.get(pk=listing_id)
    comment_form = CommentForm()
    min_bid = None
    high_bidder = None
    if len(listing.bids.all()) > 0:
        high_bidder = listing.bids.order_by("-pub_date")[0].user
    # Bids must be equal to the starting bid,
    # or greater than previously placed bids.
    if int(listing.price) == 0:
        min_bid = float(listing.starting_bid)
    else:
        min_bid = float(listing.price) + 0.01

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.all(),
        "comment_form": comment_form,
        "bids": listing.bids.all(),
        "min_bid": min_bid,
        "error_message": error_message,
        "on_watchlist": Watchlist.objects.filter(user=request.user.id, listing=listing_id),
        "creator_view": request.user == listing.creator,
        "winner": request.user == high_bidder
    })

@login_required
def bid(request, listing_id):
    """
    This view receives information about a bid on a particular listing,
    and updates the current price of the listing.This view will only process
    data recieved via POST requests, and bid submission forms only render
    on active listings, which protects against users who may try to bid
    on a closed listing. The bid HTML form uses a min attribute to specify the
    minimum allowed bid, so bids will only arrive at this view if they meet
    the requirements for new bids.
    """
    if request.method == "POST":
        amount = float(request.POST["amount"])
        listing = Listing.objects.get(pk=listing_id)
        listing.price = amount
        listing.save()
        new_bid = Bid(user=request.user, listing=listing, amount=amount)
        new_bid.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        new_comment = Comment(
            listing=listing,
            user=request.user,
            text=request.POST["text"]
        )
        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required
def close(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.user == listing.creator:
            listing.currently_active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

        else:
            return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user).order_by("-date_added")
    listings = [item.listing for item in watchlist]
    return render(request, "auctions/index.html", {
        "header": "Your Watchlist",
        "listings": listings
    })

@login_required
def watchlist_update(request, listing_id):
    """
    If a listing is on a user's watchlist, remove it.
    Otherwise, add it to the user's watchlist.
    """
    user = request.user
    current = Watchlist.objects.filter(user=user.id, listing=listing_id)
    if current:
        current.delete()
    else:
        listing = Listing.objects.get(pk=listing_id)
        new = Watchlist(user=user, listing=listing)
        new.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def categories(request):
    categories = [t[1] for t in Listing().CATEGORY_CHOICES]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category):
    listings = Listing.objects.filter(category=category.lower(), currently_active=True).order_by("-pub_date")
    return render(request, "auctions/index.html", {
        "header": f"Category: {category}",
        "listings": listings
    })
