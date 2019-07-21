from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from BookingSite.models import ROOM_TYPES, City, Hotel, Room, Reservation, User
from BookingSite.forms import SearchForm, SignInForm, SignUpForm
import datetime
from datetime import timedelta


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

def search_room(search_check_in, search_check_out, search_type, search_city):
    # Store the hotels which are located in the searching city
    hotels_in_location = Hotel.objects.filter(city=search_city)
    # Summarize the rooms which have the searching type in the specific hotel
    room_list = Room.objects.filter(hotel_id__in=hotels_in_location).filter(type=search_type)
    # Exclude the rooms which are already booked in the check in - check out period
    while True:
        booked_rooms = Reservation.objects.filter(date=search_check_in).values_list('room')
        room_list = room_list.exclude(id__in=booked_rooms)
        # print("In the search_room() function: booked rooms on {} excluded from the search result".format(search_check_in))
        search_check_in += timedelta(days=1)
        if search_check_in == search_check_out:
            break

    # List of hotels which have at least 1 room in room_list
    hotels_in_room_list = room_list.order_by('price').values_list('hotel', flat=True).order_by('hotel').distinct()

    # Eliminate the duplicate in the element of result rooms
    room_result = Room.objects.none()
    room_result |= [room_list.filter(hotel_id=id).first() for id in hotels_in_room_list]

    return room_result

def check_reservation(room, check_in, check_out, user):
    # Reservation on the specific room
    res_on_room = Reservation.objects.filter(room=room)
    # Temporary iterator used in the next loop
    date_point = check_in
    # Check if there's any reservations on the date between check_in and check_out
    while True:
        # If any reservations on that room on the date exist, return nothing
        if Reservation.objects.filter(room=room).filter(date=date_point).exists():
            print("At make_reservation(): reservation on {} found! Return None".format(date_point))
            return False
        # Update the iterator
        date_point += timedelta(days=1)
        # If checking though all of reservation days have done, go out of the loop
        if date_point == check_out:
            break
    return True
    

def make_reservation(room, check_in, check_out, user):
    books = []
    date_point = check_in
    while True:
        booking = Reservation.objects.create(date=date_point, room=room, user=user)
        print("At make_reservation(): making a new reservation on {}".format(booking))
        books.append(booking.id)
        #booking.save()
        date_point += timedelta(days=1)
        if date_point == check_out:
            break
    return books

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
    search_check_in = search_form.cleaned_data['check_in_date']
    search_check_out = search_form.cleaned_data['check_out_date']
    # Room type searching
    search_type = search_form.cleaned_data['type']
    # City searching
    search_city = City.objects.get(name=search_form.cleaned_data['city'])
    # Obtain the applicable rooms 
    room_result = search_room(search_check_in, search_check_out, search_type, search_city)

    return render(request, 'search_result.html', {'user': user, 'check_in': search_check_in, 'check_out': search_check_out, 'type': dict(ROOM_TYPES).get(search_type), 'city': search_city, 'room': room_result, 'extend_template': template_for_extends(user)})

def confirmation(request):
    user = user_object(request)
    '''
    if not Room.objects.filter(id=request.POST.get('room', None)).exists():
        return redirect(index)
    '''
    room = Room.objects.get(id=request.POST.get('room', None))
    check_in_date = datetime.datetime.strptime(request.POST.get('check_in', None), "%m.%d.%Y").date()
    check_out_date = datetime.datetime.strptime(request.POST.get('check_out', None), "%m.%d.%Y").date()

    search_form = SearchForm(cities=City.objects.all())
    search_form.fields['city'].initial = room.hotel.city
    search_form.fields['type'].initial = room.type
    search_form.fields['check_in_date'].initial = check_in_date
    search_form.fields['check_out_date'].initial = check_out_date

    return render(request, 'confirmation.html', {'user': user, 'check_in': check_in_date, 'check_out': check_out_date, 'type': dict(ROOM_TYPES).get(room.type), 'room': room, 'extend_template': template_for_extends(user), 'search_form': search_form})

def do_confirmation(request):
    user = user_object(request)
    try:
        if not user:
            raise RuntimeError("Connection timed out. Please log in again")
    except RuntimeError as e:
        return HttpResponse(str(e) + "<p><a href=index>Go back to main page</a></p>")
    room = Room.objects.filter(id=request.POST.get('room', None)).get()
    check_in_date = datetime.datetime.strptime(request.POST.get('check_in', None), "%m.%d.%Y").date()
    check_out_date = datetime.datetime.strptime(request.POST.get('check_out', None), "%m.%d.%Y").date()
    
    if check_reservation(room, check_in_date, check_out_date, user):
        books = make_reservation(room, check_in_date, check_out_date, user)
        
        price = 0
        
        for id in books:
            print("At do_confirmation(): in for loop, looking at id: {}".format(id))
            price += Reservation.objects.get(id=id).room.price
        
        return render(request, 'result.html', {'user': user, 'hotel': room.hotel, 'city': room.hotel.city, 'type': dict(ROOM_TYPES).get(room.type), 'price': price, 'check_in': check_in_date, 'check_out': check_out_date, 'proceed': True, 'extend_template': template_for_extends(user)})
    else:
        # Notice the booking has been failed
        return render(request, 'result.html', {'user': user, 'proceed': False, 'extend_template': template_for_extends(user)})

    '''
    books = make_reservation(room, check_in_date, check_out_date, user)
    if not books:
        return render(request, 'result.html', {'user': user, 'proceed': False, 'extend_template': template_for_extends(user)})
    else:
        price = 0
        for booking in books:
            booking.save()
            price += booking.priceS
    '''
    



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
