from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "bio", "agreement_accepted", "avatar"


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", )
