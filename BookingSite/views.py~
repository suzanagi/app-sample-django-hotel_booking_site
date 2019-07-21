from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from BookingSite.models import ROOM_TYPES, City, Hotel, Room, Reservation, User
from BookingSite.forms import SearchForm, SignInForm, SignUpForm
import datetime


def template_for_extends(user):
    if user: 
        return 'base_with_user.html'
    else:
        return 'base_without_user.html'

def user_object(request):
    user_id = request.session.get('authorized_user_id', None)
    if user_id:
        user = User.objects.filter(id=user_id).get()
    else:
        user = None
    return user

def search_room(search_date, search_type, search_city):
    # Store the rooms which are reserved already, on the searching date
    booked_rooms = Reservation.objects.filter(date=search_date).values_list('room')
    # Store the hotels which are located in the searching city
    hotels_in_location = Hotel.objects.filter(city=search_city)
        
    # Summarize the rooms which have the searching type, on the location, and excluding booked rooms, in the order cheaper price comes first
    r_list = Room.objects.filter(type=search_type).filter(hotel_id__in=hotels_in_location).exclude(id__in=booked_rooms).order_by('price')

    # List of hotels of the rooms which has the certain type and location
    hotels_in_r_list = r_list.values_list('hotel', flat=True).order_by('hotel').distinct()

    # Eliminate the duplicate in the element of result rooms
    room_result = Room.objects.none()
    room_result |= [r_list.filter(hotel_id=id).first() for id in hotels_in_r_list]
    return room_result

def make_reservation(room, date, user):
    if Reservation.objects.filter(room=room).filter(date=date).exists():
        return None
    else:
        booking = Reservation(room=room, date=date, user=user)
        return booking

def index(request):
    user = user_object(request)
    cities = City.objects.all()

    return render(request, 'index.html', {'user': user, 'extend_template': template_for_extends(user), 'search_form': SearchForm(cities=cities)})

def list_of_result(request):
    # Search form given by index page
    cities = City.objects.all()
    search_form = SearchForm(request.POST, cities=cities)
    try:
        if not search_form.is_valid():
            raise RuntimeError("Error: " + str(search_form.errors))
    except RuntimeError as e:
        return HttpResponse(str(e) + "<p><a href=index>Go Back</a></p>")
    # User Name who is logging in
    user = user_object(request)
    # Date searching 
    search_date = search_form.cleaned_data['date']
    # Room type searching
    search_type = search_form.cleaned_data['type']
    # City searching
    search_city = City.objects.get(name=search_form.cleaned_data['city'])
    # Obtain the applicable rooms 
    room_result = search_room(search_date, search_type, search_city)

    return render(request, 'search_result.html', {'user': user, 'date': search_date, 'type': dict(ROOM_TYPES).get(search_type), 'city': search_city, 'room': room_result, 'extend_template': template_for_extends(user)})

def confirmation(request):
    user = user_object(request)
    room = Room.objects.get(id=request.POST.get('room', None))
    date = datetime.datetime.strptime(request.POST.get('date', None), "%m.%d.%Y").date()
    
    return render(request, 'confirmation.html', {'user': user, 'date': date, 'type': dict(ROOM_TYPES).get(room.type), 'room': room, 'extend_template': template_for_extends(user)})

def do_confirmation(request):
    user = user_object(request)
    try:
        if not user:
            raise RuntimeError("Connection timed out. Please log in again")
    except RuntimeError as e:
        return HttpResponse(str(e) + "<p><a href=index>Go back to main page</a></p>")
    room = Room.objects.filter(id=request.POST.get('room', None)).get()
    date = datetime.datetime.strptime(request.POST.get('date', None), "%m.%d.%Y").date()
    booking = make_reservation(room, date, user)
    if not booking:
        return render(request, 'result.html', {'user': user, 'proceed': False, 'extend_template': template_for_extends(user)})
    else:
        booking.save()
        return render(request, 'result.html', {'user': user, 'booking': booking, 'type': dict(ROOM_TYPES).get(room.type), 'proceed': True, 'extend_template': template_for_extends(user)})

def sign_in(request):
    return render(request, 'sign_in.html', {'sign_in_form': SignInForm()})

def do_sign_in(request):
    sign_in_form=SignInForm(request.POST)
    try:
        if not sign_in_form.is_valid():
            raise RuntimeError("Error: " + str(sign_in_form.errors))
        u = User.objects.filter(email=sign_in_form.cleaned_data['email'])

        if len(u) == 0 or not check_password(sign_in_form.cleaned_data['password'], u[0].password):
            print("User Auth Failed: Wrong address or password.")
            raise RuntimeError("Wrong email address or password.")
        request.session['authorized_user_id'] = u[0].id
    except RuntimeError as e:
        return HttpResponse(str(e) + "<p><a href=sign_in>Go back</a></p>")
    return redirect('index')
    
def do_sign_out(request):
    request.session['authorized_user_id'] = None
    print("session user: {}".format(request.session['authorized_user_id']))
    return redirect('index')
    
def sign_up(request):
    return render(request, 'sign_up.html', {'sign_up_form': SignUpForm()})

def do_sign_up(request):
    sign_up_form = SignUpForm(request.POST)

    try:
        if not sign_up_form.is_valid():
            raise RuntimeError("Error: " + str(sign_up_form.errors))

        values = sign_up_form.cleaned_data

        if len(User.objects.filter(email=values['email'])) > 0:
            raise RuntimeError("An user with the email '{}' already exists.".format(values['email']))
        if values['password'] != values['passconf']:
            raise RuntimeError("Passwords do not match.")

        User.objects.create(f_name=values['f_name'], m_name=values['m_name'], l_name=values['l_name'], email=values['email'], password=make_password(values['password']))

    except RuntimeError as e:
        return HttpResponse(str(e) + "<p><a href=sign_up>Go back</a></p>")
    
    return redirect('index')
