from django.contrib import admin
from .models import OrchestralProject, MusicalProgram, Instrument, AcademicPeriod, MusicalCenter, Student, EmergencyContact, StudentRelative, DetailAcademicInscription, Employee, AdminPosition, AdminCollateral

# Register your models here.
admin.site.register(OrchestralProject)
admin.site.register(MusicalProgram)
admin.site.register(Instrument)
admin.site.register(AcademicPeriod)
admin.site.register(MusicalCenter)
admin.site.register(Student)
admin.site.register(StudentRelative)
admin.site.register(DetailAcademicInscription)
admin.site.register(EmergencyContact)
admin.site.register(Employee)
admin.site.register(AdminPosition)
admin.site.register(AdminCollateral)