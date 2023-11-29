from django.contrib import admin

from .models import Enterprise, Country, EmployeeStatusLog, EmployeeRoom, Room, Face, SecurityCode, Qr, Employee, Role, \
    EnterpriseAdmin, EnterpriseAdminRole,EconomicSector

admin.site.register(Enterprise)
admin.site.register(Country)
admin.site.register(EnterpriseAdmin)
admin.site.register(Role)
admin.site.register(Employee)
admin.site.register(Qr)
admin.site.register(SecurityCode)
admin.site.register(Face)
admin.site.register(Room)
admin.site.register(EmployeeRoom)
admin.site.register(EmployeeStatusLog)
admin.site.register(EnterpriseAdminRole)
admin.site.register(EconomicSector)

