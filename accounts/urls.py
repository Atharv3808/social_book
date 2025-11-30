from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    # Route the main login to two-step login (normal login removed)
    path("login/", views.two_step_login, name="login"),
    # Two-step login flow
    path("login-2step/", views.two_step_login, name="login_two_step"),
    path("login-2step/verify/", views.two_step_verify, name="login_two_step_verify"),
    # Use a simple view that accepts GET so the navbar logout link works without JS
    path("logout/", views.logout_view, name="logout"),
    # Authors & Sellers listing page
    path("authors-sellers/", views.authors_sellers, name="authors_sellers"),
    # Upload Books dashboard
    path("upload-books/", views.upload_books_dashboard, name="upload_books"),
    # My Books dashboard (requires user to have uploads)
    path("my-books/", views.my_books_dashboard, name="my_books"),
    # Session-authenticated download for My Books page
    path("download/<int:pk>/", views.download_my_book, name="download_my_book"),
]
