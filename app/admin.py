from django.contrib import admin

# Register your models here.
from .models import OrchestralProject, MusicalProgram, Instrument, AcademicPeriod, MusicalCenter

# Register your models here.
admin.site.register(OrchestralProject)
admin.site.register(MusicalProgram)
admin.site.register(Instrument)
admin.site.register(AcademicPeriod)
admin.site.register(MusicalCenter)