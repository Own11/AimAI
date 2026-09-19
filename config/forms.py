from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import get_user_model


class SignupForm(AllauthSignupForm):
    """Normalize email and remove only stale allauth email rows."""

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Аккаунт с этим email уже существует.')
        stale = EmailAddress.objects.filter(email__iexact=email, user__isnull=True)
        stale.delete()
        return email
