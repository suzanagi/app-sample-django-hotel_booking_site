from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from BookingSite.models import ROOM_TYPES, Reservation

class SearchForm(forms.Form):
    city = forms.ChoiceField(label='Location')
    type = forms.ChoiceField(label='Room Type')
    check_in_date = forms.DateField(widget = DatePickerInput(format='%Y-%m-%d'))
    check_out_date = forms.DateField(widget = DatePickerInput(format='%Y-%m-%d'))
    
    '''
    check_in_date = forms.DateField(label='Check in')
    check_out_date = forms.DateField(label='Check out')
    '''
    
    def __init__(self, *args, **kwargs):
        cities = kwargs.pop('cities')
        super().__init__(*args, **kwargs)

        self.fields['city'].choices = zip(cities, cities)
        self.fields['type'].choices = ROOM_TYPES

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
