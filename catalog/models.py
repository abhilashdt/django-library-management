from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=180)
    author = models.CharField(max_length=120)
    isbn = models.CharField(max_length=20, unique=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} — {self.author}"


class Member(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Loan(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, related_name="loans"
    )
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="loans"
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.book.title} → {self.member.name}"
