from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    # Add this field to match what your template is expecting
    ROLE_CHOICES = [
        ("Farmer", "Farmer"),
        ("Technician", "Technician"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="User Role",
        help_text="Select whether you want to register as a Farmer or Technician.",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2", "role"]


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["email"]
