from django import forms
from BookingSite.models import ROOM_TYPES, Reservation

class SearchForm(forms.Form):
    city = forms.ChoiceField(label='Location')
    type = forms.ChoiceField(label='Room Type')
    check_in_date = forms.DateField(label='Check in')
    check_out_date = forms.DateField(label='Check out')
    
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop('cities')
        super().__init__(*args, **kwargs)

        self.fields['city'].choices = zip(cities, cities)
        self.fields['type'].choices = ROOM_TYPES

class SignInForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=320)
    password = forms.CharField(label='Password', max_length=20, widget=forms.PasswordInput())

class SignUpForm(forms.Form):
    f_name = forms.CharField(label='First Name', max_length=16)
    m_name = forms.CharField(label='Middle Name (Optional)', max_length=16, required=False)
    l_name = forms.CharField(label='Last Name', max_length=16)
    email = forms.EmailField(label='Email', max_length=320)
    password = forms.CharField(label='Password', max_length=20, widget=forms.PasswordInput())
    passconf = forms.CharField(label='Re-enter Password', max_length=20, widget=forms.PasswordInput())
