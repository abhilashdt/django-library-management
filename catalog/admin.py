from django.contrib import admin
from .models import Book, Loan, Member


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "isbn", "total_copies", "available_copies"
    )
    search_fields = ("title", "author", "isbn")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "book", "member", "issued_at", "due_date", "returned_at"
    )
    list_filter = ("due_date", "returned_at")
    search_fields = ("book__title", "member__name", "member__email")
