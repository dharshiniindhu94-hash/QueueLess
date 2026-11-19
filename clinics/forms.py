from django import forms
from django.contrib.auth import get_user_model
from .models import Clinic, Doctor

User = get_user_model()


class ClinicForm(forms.ModelForm):

    class Meta:
        model = Clinic
        fields = [
            'clinic_name',
            'address',
            'contact_number',
            'opening_time',
            'closing_time',
            'is_active',
        ]

        widgets = {
            'clinic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter clinic name'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter clinic address'
            }),

            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),

            'opening_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),

            'closing_time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        opening = cleaned_data.get('opening_time')
        closing = cleaned_data.get('closing_time')

        if opening and closing and closing <= opening:
            raise forms.ValidationError(
                'Closing time must be later than opening time.'
            )

        return cleaned_data




class DoctorForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    specialization = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    clinic = forms.ModelChoiceField(
        queryset=Clinic.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    average_consultation_minutes = forms.IntegerField(
        min_value=1,
        max_value=120,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

class DoctorEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    specialization = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    clinic = forms.ModelChoiceField(
        queryset=Clinic.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    average_consultation_minutes = forms.IntegerField(
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
