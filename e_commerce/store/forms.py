# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django.forms import ModelForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email']