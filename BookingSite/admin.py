from django.contrib import admin
from BookingSite.models import City, Hotel, Room, User, Reservation

class CityAdmin(admin.ModelAdmin):
    list_display = ['name']

class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']

class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'type', 'price']

class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'password']
    fields = ['f_name', 'l_name', 'm_name', 'email', 'password']

    def name(self, instance):
        return instance.__str__()

class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'room_type', 'date', 'price']

    def hotel(self, instance):
        return instance.room.hotel

    def room_type(self, instance):
        return instance.room.get_type_display()

    def price(self, instance):
        return instance.room.price

admin.site.register(City, CityAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Reservation, ReservationAdmin)

