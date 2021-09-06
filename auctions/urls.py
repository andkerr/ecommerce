from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist_update/<int:listing_id>", views.watchlist_update, name="watchlist_update"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.category_listings, name="category_listings")
]
