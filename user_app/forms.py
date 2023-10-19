from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'})
    )
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']