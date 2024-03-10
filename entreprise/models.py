from abc import ABC

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.base_user import BaseUserManager

from account.models import Custom_User

continent_choices = [
    ('AFRIQUE', 'Afrique'),
    ('EUROPE', 'Europe'),
    ('AMERIQUE', 'Amerique'),
    ('OCEANIE', 'Océanie'),
    ('ASIE', 'Asie'),
]

CARD_TYPES = [
        ('PASSPORT', 'Passport'),
        ('CNI', 'CNI'),
        ('CIP', 'CIP'),
        ("AUTRES","AUTRES")
    ]

role_type_choices = [
        ('ADMINISTRATION', 'Administration'),
        ('SOFTWARE', 'Software'),
    ]

SEXE_CHOICES=(
    ("HOMME", "HOMME"),
    ("FEMME", "FEMME"),
    ("AUTRES","AUTRES")
)

ACCESS_MODE = [
    ('Qr code',"Qr Code"), 
    ('Security code', "Code de Sécurity"),
    ('Face','Visage')
]

REQUEST_TYPES = [
    ('LEAVE', 'Leave'),
    ('PERMISSION', 'Permission'),
    ('DOCUMENT_COPY', 'Document Copy'),
    ('MODIFY_EMPLOYEE_DATA', 'Modify Employee Data'),
]

DOCUMENT_TYPES = [
    ('WORK_CERTIFICATE', 'Work Certificate'),
    ('EMPLOYMENT_CONTRACT', 'Employment Contract'),
    ('PAYSLIP', 'Payslip'),
]

LEAVE_TYPES = [
    ('ANNUAL_LEAVE', 'Annual Leave'),
    ('SICK_LEAVE', 'Sick Leave'),
    ('UNPAID_LEAVE', 'Unpaid Leave'),
]

TYPE_EVENEMENTS = [
    ('ARRIVEE', 'Arrival'),
    ('DEPART', 'Departure'),
]

TYPE_MODIFICATION_DATA_EMPLOYE = [
    ('PICTURE', 'Picture'),
    ('QR_CODE', 'QR Code'),
    ('SECURITY_CODE', 'Security Code'),
]

#Base modelClass
class ModelBasic():
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

###############################  Country class  ################################################
class Country(models.Model,ModelBasic):
    continent = models.CharField(max_length=255, choices=continent_choices)
    name = models.CharField(max_length=255),
    indicatif = models.CharField(max_length=255)
    iso_code = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.continent}  {self.name}"

#############################   Role class  #####################################################"
class Role(models.Model):
    __metaclass__ = ModelBasic

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=role_type_choices, default='Administration')
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

################################################## Economic sector ##################################""
class EconomicSector(models.Model):
    __metaclass__ = ModelBasic
    sectorname = models.CharField(max_length=255, default="") 
    sectordesciption = models.CharField(max_length=255, default= "")
    
    
######################################## Enterprise class ###################################################""
class Enterprise(models.Model):
    __metaclass__ = ModelBasic
    email = models.EmailField(verbose_name='email adress',
                              max_length=255,default="nothin@gmail.com"
                              ) 
    creator = models.ForeignKey(Custom_User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ifu = models.CharField(max_length=255, default=" ")
    rcm = models.CharField(max_length=255, default=" ")
    director_card_id = models.CharField(max_length=255, default=" ")
    director_card_file = models.ImageField(default='default_rccm.png', upload_to='statics/')
    rccm_file = models.ImageField(default='default.png', upload_to='statics/')
    director_card_type = models.CharField(max_length=255, choices=CARD_TYPES, default='CNI')
    director_fullname = models.CharField(max_length=255, default="String"), 
    director_lastname = models.CharField(max_length=255, default="String")  # Corrected field name
    director_firstname = models.CharField(max_length=255, default="String")  # Corrected field name
    phone = models.CharField(max_length=255, default="String")
    is_approved = models.BooleanField(default=False)
    logo = models.ImageField(default='default_logo.png', upload_to='statics/')
    status = models.IntegerField(default=0)
    description = models.CharField(max_length=255, default='String')
    adress = models.CharField(max_length=255, default='String')
    request_to_use = models.CharField(max_length=255, default=" ")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default=1)
    sectors =models.ManyToManyField(EconomicSector,default=1)

    def __str__(self):
        return f"{self.name}"


##########################  class Employee  ##################################
class Employee(models.Model):
    user = models.OneToOneField(Custom_User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    date_created_at = models.DateTimeField(auto_now_add=True)
    date_updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user}"
##############################  Entreprise Admin    ###################################
class EnterpriseAdmin(models.Model):
    __metaclass__ = ModelBasic
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    job = models.CharField(max_length=100,default = "String")
    job_description = models.CharField(max_length=100,default = "String")
    enterprises = models.ManyToManyField(Enterprise,)
    roles = models.ManyToManyField(Role)

    def __str__(self):
        return f"The employee n°{self.employee} is admin" 


################################# Entreprise admin rôle     ################################"

class EnterpriseAdminRole(models.Model):
    __metaclass__ = ModelBasic
    is_active = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    entreprise_admin = models.ForeignKey(EnterpriseAdmin, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise,on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.role}"





################################# Class Qr  ############################

class Qr(models.Model):
    __metaclass__ = ModelBasic
    is_current = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=255)
    qr_image = models.ImageField(default="default.png", upload_to='statics/')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.qr_code



##################################  Classe Security Code ####################

class SecurityCode(models.Model):
    __metaclass__ = ModelBasic
    is_current = models.BooleanField(default=False)
    code = models.CharField(max_length=255,unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date_created_at = models.DateTimeField(auto_now_add=True)
    date_updated_at = models.DateTimeField(auto_now=True)


############################### class Face   ###############################
class Face(models.Model):
    __metaclass__ = ModelBasic
    is_main = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    face_file = models.FileField(default="default.png", upload_to='statics/')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.face_file}"



############################### class Room ####################################

class Room(models.Model):
    __metaclass__ = ModelBasic
    designation = models.CharField(max_length=255)
    check_security_code = models.BooleanField(default=False)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.designation}"


############################# class Employee Room ###################################################
class EmployeeRoom(models.Model):
    __metaclass__ = ModelBasic
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    date_add_at = models.DateTimeField(auto_now_add=True)
    date_updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"{self.room.designation}"

#################################### Employee status class  ###########################

class EmployeeStatusLog(models.Model):
    __metaclass__ = ModelBasic
    status = models.BooleanField(default=False)
    employee_log = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee_log}" 
    



################################## Access Model #################################################### 
class AccesModel (models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE) 
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    access_mode = models.CharField(max_length=255,choices = ACCESS_MODE, default ='Visage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


############################# LeaveRequest  Model (Congées) ################################"
class LeaveRequest(models.Model,ModelBasic):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE) 
    enterprise = models.ForeignKey(Enterprise,on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default = "Sick Leave") 
    reason = models.TextField()
    start_at = models.DateField()
    end_at = models.DateField()
    is_approuve = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Permission Request #{self.leave_type}" 
    
    
################################  Break Request  (Pause) ################################
class BreakRequest(models.Model, ModelBasic):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    reason = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Break Request #{self.id}" 
    
################################# Permission Request (Permission urgent) ################## 
class PermissionRequest(models.Model, ModelBasic):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    reason = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_approved = models.BooleanField(default=False) 
    
    def __str__(self):
        return f"Permission Request #{self.id}"
 
 
 ############################## Document Copy Request (Demander les copies des documents) ################################## 
class DocumentCopyRequest(models.Model, ModelBasic):
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES,default = "Work Certificate")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE) 
    comment = models.TextField()
    
    def __str__(self):
        return f"Document Copy Request #{self.id}" 
    

######################################## Modify Employee Data Request############################
class ModifyEmployeeDataRequest(models.Model, ModelBasic):
    type_modification = models.CharField(max_length=20, choices = TYPE_MODIFICATION_DATA_EMPLOYE,default = "picture")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE) 
    new_data = models.CharField(max_length=255)
    document = models.FileField(upload_to='employee_data_requests/', null=True, blank=True)
    reason = models.TextField()

    def __str__(self):
        return f"Modify Employee Data Request #{self.id}"
 


#################################### Shedule Form ###############################################
class EnterpriseScheduleEnter(models.Model, ModelBasic):
    start_at = models.DateField()
    end_at = models.DateField()
    task_to_do = models.TextField()
    comment = models.TextField()

    def __str__(self):
        return f"Enterprise Schedule enter #{self.id}" 
    

class EnterpriseSchedule(models.Model, ModelBasic):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    #schedule_enter = models.ManyToManyField(EnterpriseScheduleEnter,default = [])
    start_at = models.DateField()
    end_at = models.DateField()
    task_to_do = models.TextField()
    comment = models.TextField()

    def __str__(self):
        return f"Enterprise Schedule #{self.id}"