from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookForm, IssueBookForm, MemberForm
from .models import Book, Loan, Member
from .services import issue_book, return_book


def dashboard(request):
    context = {
        "book_count": Book.objects.count(),
        "member_count": Member.objects.count(),
        "active_loan_count": Loan.objects.filter(
            returned_at__isnull=True
        ).count(),
        "recent_loans": Loan.objects.select_related(
            "book", "member"
        )[:5],
    }
    return render(request, "catalog/dashboard.html", context)


def book_list(request):
    books = Book.objects.all()
    return render(request, "catalog/book_list.html", {"books": books})


def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect("book_list")
    return render(request, "catalog/book_form.html", {"form": form})


def member_list(request):
    members = Member.objects.all()
    return render(request, "catalog/member_list.html", {"members": members})


def member_create(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member registered successfully.")
        return redirect("member_list")
    return render(request, "catalog/member_form.html", {"form": form})


def loan_list(request):
    loans = Loan.objects.select_related("book", "member").all()
    return render(request, "catalog/loan_list.html", {"loans": loans})


def issue_book_view(request):
    form = IssueBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            issue_book(
                book_id=data["book"].pk,
                member_id=data["member"].pk,
                due_date=data["due_date"],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Book issued successfully.")
            return redirect("loan_list")
    return render(request, "catalog/issue_book.html", {"form": form})


@require_POST
def return_book_view(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    try:
        return_book(loan_id=loan.pk)
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    else:
        messages.success(request, "Book returned successfully.")
    return redirect("loan_list")
