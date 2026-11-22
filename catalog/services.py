from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Book, Loan, Member


@transaction.atomic
def issue_book(*, book_id, member_id, due_date):
    book = Book.objects.select_for_update().get(pk=book_id)
    member = Member.objects.get(pk=member_id)

    if book.available_copies < 1:
        raise ValidationError("No copies are currently available.")

    already_active = Loan.objects.filter(
        book=book,
        member=member,
        returned_at__isnull=True,
    ).exists()
    if already_active:
        raise ValidationError(
            "This member already has an active loan for this book."
        )

    loan = Loan.objects.create(
        book=book,
        member=member,
        due_date=due_date,
    )
    book.available_copies -= 1
    book.save(update_fields=["available_copies"])
    return loan


@transaction.atomic
def return_book(*, loan_id):
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    if loan.returned_at is not None:
        raise ValidationError("This loan has already been returned.")

    book = Book.objects.select_for_update().get(pk=loan.book_id)
    if book.available_copies >= book.total_copies:
        raise ValidationError("Inventory count is already at its maximum.")

    loan.returned_at = timezone.now()
    loan.save(update_fields=["returned_at"])

    book.available_copies += 1
    book.save(update_fields=["available_copies"])
    return loan
