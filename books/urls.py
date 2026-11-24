from django.urls import path
from . import views
app_name = "books"
urlpatterns = [
    path("add/", views.add_book, name="book-add"),
    # (optional) a simple list view:
     path("", views.book_list, name="book-list"),
]
