from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.book_create, name="book_create"),
    path("members/", views.member_list, name="member_list"),
    path("members/add/", views.member_create, name="member_create"),
    path("loans/", views.loan_list, name="loan_list"),
    path("loans/issue/", views.issue_book_view, name="issue_book"),
    path(
        "loans/<int:loan_id>/return/",
        views.return_book_view,
        name="return_book",
    ),
]
