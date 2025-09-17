from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Roles.choices, required=True, label="Role")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        from .models import Article
        model = Article
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Headline"}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Write your article..."}),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        from .models import Newsletter
        model = Newsletter
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Newsletter title"}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Compose your newsletter..."}),
        }
