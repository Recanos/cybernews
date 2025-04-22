from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm, LoginForm
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CustomLoginForm(LoginForm):
    """
    Кастомная форма входа, которая позволяет входить как по логину, так и по email.
    """
    login = forms.CharField(
        label="Логин или Email",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин или Email'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )

    error_messages = {
        'invalid_login': "Пожалуйста, введите правильный логин/email и пароль. Обратите внимание, что оба поля могут быть чувствительны к регистру.",
        'inactive': "Этот аккаунт неактивен.",
        'email_password_mismatch': "Неверный email или пароль.",
        'username_password_mismatch': "Неверный логин или пароль.",
        'username_email_password_mismatch': "Неверный логин/email или пароль.",
    }

    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for login.
        """
        credentials = {}
        login = self.cleaned_data["login"]
        password = self.cleaned_data["password"]

        # Определяем, является ли введенное значение email или логином
        if "@" in login:
            credentials["email"] = login
        else:
            credentials["username"] = login

        credentials["password"] = password
        return credentials

class CustomSignupForm(SignupForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Логин",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )

    def save(self, request):
        user = super().save(request)
        return user 