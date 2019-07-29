from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from BookingSite.models import ROOM_TYPES, Reservation
import datetime
from datetime import timedelta

class SearchForm(forms.Form):
    city = forms.ChoiceField(label='Location')
    type = forms.ChoiceField(label='Room Type')

    check_in_date = forms.DateField(
        widget = DatePickerInput(
            options={
                "format": "YYYY-MM-DD", 
                "defaultDate": str(datetime.date.today()), 
                "minDate": str(datetime.date.today()), 
                "maxDate": str(datetime.date.today() + timedelta(days=14)),
                }
            )
        )
    
    check_out_date = forms.DateField(
        widget = DatePickerInput(
            options={
                "format": "YYYY-MM-DD", 
                "defaultDate": str(datetime.date.today() + timedelta(days=1)), 
                "minDate": str(datetime.date.today() + timedelta(days=1)), 
                "maxDate": str(datetime.date.today() + timedelta(days=15)),
                }
            )
        )

    def __init__(self, *args, **kwargs):
        cities = kwargs.pop('cities')
        super().__init__(*args, **kwargs)

        self.fields['city'].choices = zip(cities, cities)
        self.fields['type'].choices = ROOM_TYPES

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get("check_in_date")
        check_out_date = cleaned_data.get("check_out_date")
        if check_in_date and check_out_date:
            if (check_out_date - check_in_date) < timedelta(days=1):
                raise forms.ValidationError("Check out date must not be same or earliar than check in date!")

class SignInForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=320)
    password = forms.CharField(label='Password', max_length=20, widget=forms.PasswordInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder']='Email Address'
        self.fields['password'].widget.attrs['placeholder']='Enter Password'

class SignUpForm(forms.Form):
    f_name = forms.CharField(label='First Name', max_length=16)
    m_name = forms.CharField(label='Middle Name (Optional)', max_length=16, required=False)
    l_name = forms.CharField(label='Last Name', max_length=16)
    email = forms.EmailField(label='Email', max_length=320)
    password = forms.CharField(label='Password', max_length=20, widget=forms.PasswordInput())
    passconf = forms.CharField(label='Re-enter Password', max_length=20, widget=forms.PasswordInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['f_name'].widget.attrs['placeholder']='First Name'
        self.fields['m_name'].widget.attrs['placeholder']='Middle Name'
        self.fields['l_name'].widget.attrs['placeholder']='Last Name(Family Name)'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address'
        self.fields['password'].widget.attrs['placeholder']='Enter Password'
        self.fields['passconf'].widget.attrs['placeholder']='Enter Password Again'
