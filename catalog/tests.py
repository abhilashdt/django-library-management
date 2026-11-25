from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .forms import BookForm, MemberForm
from .models import Book, Loan, Member
from .services import issue_book, return_book


class ModelTests(TestCase):
    def test_book_str(self):
        book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            total_copies=3,
            available_copies=3,
        )
        self.assertEqual(str(book), "Clean Code — Robert C. Martin")

    def test_member_str(self):
        member = Member.objects.create(
            name="Alice Smith",
            email="alice@example.com",
            phone="1234567890",
        )
        self.assertEqual(str(member), "Alice Smith")

    def test_loan_str(self):
        book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            isbn="9780201485677",
            total_copies=1,
            available_copies=1,
        )
        member = Member.objects.create(
            name="Bob Jones",
            email="bob@example.com",
            phone="0987654321",
        )
        loan = Loan.objects.create(
            book=book,
            member=member,
            due_date=date.today() + timedelta(days=14),
        )
        self.assertEqual(str(loan), "Refactoring → Bob Jones")


class FormTests(TestCase):
    def test_book_form_valid(self):
        form = BookForm(
            data={
                "title": "Design Patterns",
                "author": "GoF",
                "isbn": "9780201633610",
                "total_copies": 5,
                "available_copies": 5,
            }
        )
        self.assertTrue(form.is_valid())

    def test_book_form_available_exceeds_total(self):
        form = BookForm(
            data={
                "title": "Invalid Book",
                "author": "Test",
                "isbn": "1234567890",
                "total_copies": 2,
                "available_copies": 5,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("available_copies", form.errors)

    def test_member_form_valid(self):
        form = MemberForm(
            data={
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "phone": "555-1234",
            }
        )
        self.assertTrue(form.is_valid())


class LoanServiceTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Python Basics",
            author="A. Writer",
            isbn="978000000001",
            total_copies=2,
            available_copies=2,
        )
        self.member = Member.objects.create(
            name="Sam Reader",
            email="sam@example.com",
            phone="5550100",
        )
        self.due_date = date.today() + timedelta(days=7)

    def test_issue_reduces_stock(self):
        issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=self.due_date,
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

    def test_return_restores_stock(self):
        loan = issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=self.due_date,
        )
        return_book(loan_id=loan.pk)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

    def test_cannot_issue_when_no_stock(self):
        self.book.available_copies = 0
        self.book.save(update_fields=["available_copies"])
        with self.assertRaises(ValidationError):
            issue_book(
                book_id=self.book.pk,
                member_id=self.member.pk,
                due_date=self.due_date,
            )

    def test_cannot_return_twice(self):
        loan = issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=self.due_date,
        )
        return_book(loan_id=loan.pk)
        with self.assertRaises(ValidationError):
            return_book(loan_id=loan.pk)

    def test_duplicate_active_loan_is_rejected(self):
        issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=self.due_date,
        )
        with self.assertRaises(ValidationError):
            issue_book(
                book_id=self.book.pk,
                member_id=self.member.pk,
                due_date=self.due_date,
            )

    def test_return_when_inventory_already_max(self):
        loan = Loan.objects.create(
            book=self.book,
            member=self.member,
            due_date=self.due_date,
        )
        with self.assertRaises(ValidationError):
            return_book(loan_id=loan.pk)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(
            title="Pragmatic Programmer",
            author="Hunt & Thomas",
            isbn="9780201616224",
            total_copies=2,
            available_copies=2,
        )
        self.member = Member.objects.create(
            name="Diana Prince",
            email="diana@example.com",
            phone="5550200",
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Library Management System")

    def test_book_list_view(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pragmatic Programmer")

    def test_book_create_view_get(self):
        response = self.client.get(reverse("book_create"))
        self.assertEqual(response.status_code, 200)

    def test_book_create_view_post_valid(self):
        response = self.client.post(
            reverse("book_create"),
            {
                "title": "Code Complete",
                "author": "Steve McConnell",
                "isbn": "9780735619678",
                "total_copies": 3,
                "available_copies": 3,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title="Code Complete").exists())

    def test_book_create_view_post_invalid(self):
        response = self.client.post(
            reverse("book_create"),
            {
                "title": "",
                "author": "Steve McConnell",
                "isbn": "9780735619678",
                "total_copies": 3,
                "available_copies": 3,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_member_list_view(self):
        response = self.client.get(reverse("member_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Diana Prince")

    def test_member_create_view_get(self):
        response = self.client.get(reverse("member_create"))
        self.assertEqual(response.status_code, 200)

    def test_member_create_view_post_valid(self):
        response = self.client.post(
            reverse("member_create"),
            {
                "name": "Bruce Wayne",
                "email": "bruce@example.com",
                "phone": "5550300",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Member.objects.filter(name="Bruce Wayne").exists())

    def test_member_create_view_post_invalid(self):
        response = self.client.post(
            reverse("member_create"),
            {"name": "", "email": "not-an-email", "phone": "123"},
        )
        self.assertEqual(response.status_code, 200)

    def test_loan_list_view(self):
        response = self.client.get(reverse("loan_list"))
        self.assertEqual(response.status_code, 200)

    def test_issue_book_view_get(self):
        response = self.client.get(reverse("issue_book"))
        self.assertEqual(response.status_code, 200)

    def test_issue_book_view_post_valid(self):
        response = self.client.post(
            reverse("issue_book"),
            {
                "book": self.book.pk,
                "member": self.member.pk,
                "due_date": (date.today() + timedelta(days=14)).isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Loan.objects.count(), 1)

    def test_issue_book_view_post_invalid_validation_error(self):
        issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=date.today() + timedelta(days=14),
        )
        response = self.client.post(
            reverse("issue_book"),
            {
                "book": self.book.pk,
                "member": self.member.pk,
                "due_date": (date.today() + timedelta(days=14)).isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This member already has an active loan for this book."
        )

    def test_return_book_view(self):
        loan = issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=date.today() + timedelta(days=14),
        )
        response = self.client.post(
            reverse("return_book", kwargs={"loan_id": loan.pk})
        )
        self.assertEqual(response.status_code, 302)
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)

    def test_return_book_view_already_returned(self):
        loan = issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=date.today() + timedelta(days=14),
        )
        return_book(loan_id=loan.pk)
        response = self.client.post(
            reverse("return_book", kwargs={"loan_id": loan.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_return_book_view_get_method_not_allowed(self):
        loan = issue_book(
            book_id=self.book.pk,
            member_id=self.member.pk,
            due_date=date.today() + timedelta(days=14),
        )
        response = self.client.get(
            reverse("return_book", kwargs={"loan_id": loan.pk})
        )
        self.assertEqual(response.status_code, 405)
