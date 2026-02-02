from django.db import models
from django.core.exceptions import ValidationError
from app.models import Student
import re

class EmergencyContact(models.Model):
    fullname = models.CharField(
        max_length=100,
        verbose_name="Nombre completo",
        help_text="Nombre completo del contacto de emergencia."
    )
    relationship = models.CharField(
        max_length=50, 
        verbose_name="Parentesco",
        help_text="Parentesco del contacto de emergencia."
    )
    cellphone = models.CharField(
        max_length=11, 
        verbose_name="Teléfono",
        help_text="Teléfono del contacto de emergencia."
    )
    id_student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='emergency_contacts'
    )

    def __str__(self):
        return f"{self.fullname} ({self.relationship})"
    
    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"

    def clean(self):
        super().clean()

        # Validación para cellphone (si no son nulos):
        if self.cellphone: # Check if the field has a value before applying regex
            if self.cellphone and not re.fullmatch(r'^\d{11}$', self.cellphone):
                raise ValidationError({'cellphone': 'El número de teléfono debe ser una cadena de 11 dígitos numéricos.'})