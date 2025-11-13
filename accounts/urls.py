from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    # Use our themed LoginView so form widgets get Bootstrap classes
    path("login/", views.ThemedLoginView.as_view(), name="login"),
    # Use a simple view that accepts GET so the navbar logout link works without JS
    path("logout/", views.logout_view, name="logout"),
    # Authors & Sellers listing page
    path("authors-sellers/", views.authors_sellers, name="authors_sellers"),
]
