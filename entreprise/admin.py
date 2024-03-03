from django.contrib import admin

from .models import AccesModel, BreakRequest, DocumentCopyRequest, Enterprise, Country, EmployeeStatusLog, EmployeeRoom, LeaveRequest, ModifyEmployeeDataRequest, PermissionRequest, Room, Face, SecurityCode, Qr, Employee, Role, \
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
admin.site.register(AccesModel)
admin.site.register(BreakRequest)
admin.site.register(PermissionRequest)
admin.site.register(DocumentCopyRequest)
admin.site.register(ModifyEmployeeDataRequest)
admin.site.register(LeaveRequest)




