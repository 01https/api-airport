from django.contrib import admin
from airport.models import *


admin.site.register(Airport)
admin.site.register(Airplane)
admin.site.register(AirplaneType)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(Crew)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class Admin(admin.ModelAdmin):
    inlines = [TicketInLine]
    
