import os

from django.core.mail import EmailMessage
from .models import Custom_User, Enterprise, Employee, EnterpriseAdmin, EnterpriseAdminRole


class Util:
    @staticmethod
    def send_mail(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data['to_email']]
        )
        email.send() 
        
        

def check_access(user_id, enterprise_id, droit):
    try:
        enterprise_creator = Enterprise.objects.get(id=enterprise_id, creator__id=user_id)
        return True
    except Enterprise.DoesNotExist:
        try:
            employee = Employee.objects.get(user__id=user_id, enterprise__id=enterprise_id)
            try:
                # Vérifier si l'employé est un administrateur de l'entreprise
                enterprise_admin = EnterpriseAdmin.objects.get(employee=employee)
                
                try:
                    # Vérifier si l'administrateur a le droit spécifié
                    role = EnterpriseAdminRole.objects.get(
                        entreprise_admin=enterprise_admin,
                        role=droit,
                        enterprise__id=enterprise_id
                    )
                    return role.is_active
                except EnterpriseAdminRole.DoesNotExist:
                    return False
                
            except EnterpriseAdmin.DoesNotExist:
                return False
        
        except Employee.DoesNotExist:
            return False

