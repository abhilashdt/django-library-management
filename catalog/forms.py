from django import forms
from .models import Book, Member


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "isbn",
            "total_copies",
            "available_copies",
        )

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get("total_copies")
        available = cleaned_data.get("available_copies")
        if total is not None and available is not None and available > total:
            self.add_error(
                "available_copies",
                "Available copies cannot exceed total copies.",
            )
        return cleaned_data


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ("name", "email", "phone")


class IssueBookForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Book.objects.none())
    member = forms.ModelChoiceField(queryset=Member.objects.none())
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["book"].queryset = Book.objects.filter(available_copies__gt=0)
        self.fields["member"].queryset = Member.objects.all()
