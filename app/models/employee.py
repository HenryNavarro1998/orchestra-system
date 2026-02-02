from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

DOCUMENT_TYPE_CHOICES = [
    ('V', 'Venezolano/a'),
    ('E', 'Extranjero/a'),
]

GENDER_CHOICES = [
    ('F', 'Femenino'),
    ('M', 'Masculino'),
]

TYPE_CHOICES = [
    ('FI', 'Maestro'),
    ('FT', 'Administrativo'),
    ('OT', 'Obrero'),
    ('JB', 'Jubilado'),
    ('PE', 'Pensionado'),
    ('80', 'Formador Medio Tiempo'),
    ('160','Formador Dedicación Exclusiva')
]


class Employee(models.Model):

    code = models.CharField(
        max_length=9,
        blank=True,
        unique=True,
        help_text="Código del trabajador."
    )

    document_id = models.CharField(
        max_length=8,
        blank=True,
        unique=True,
        help_text="Cédula o Pasaporte del trabajador."
    )

    names = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nombres del trabajador."
    )

    lastnames = models.CharField(
        max_length=100,
        blank=True,
        help_text="Apellidos del trabajador."
    )

    born_date = models.DateField(
        help_text="Fecha de nacimiento del trabajador"
    )

    id_admin_position = models.ForeignKey('app.AdminPosition', null=False, on_delete=models.CASCADE)

    id_admin_collateral = models.ForeignKey('app.AdminCollateral', null=False, on_delete=models.CASCADE)

    id_musical_center = models.ForeignKey('app.MusicalCenter', null=True, on_delete=models.CASCADE)

    admission_date = models.DateField(
        help_text="Fecha de ingreso del trabajador"
    )

    proffesional = models.BooleanField(default=False)

    type = models.CharField(
        max_length=20,
        help_text="Tipo de trabajador."
    )

    nationality = models.CharField(
        max_length=1,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text="Nacionalidad del trabajador ('V' para Venezolano, 'E' para Extranjero)."
    )
    
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        help_text="Género del trabajador."
    )

    class Meta:
        verbose_name = "Trabajador"
        verbose_name_plural = "Trabajadores"

    def clean(self):
        super().clean()

        # Validación para born_date:
        if self.born_date: 
            today = timezone.now().date()
            min_born_date = today - timezone.timedelta(days=16 * 365.25)  # Aproximación de 16 años
            if self.born_date and self.born_date > min_born_date:
                raise ValidationError({'born_date': 'El trabajador debe tener más de 16 años.'})
 
            
    def __str__(self):
        return f"{self.names} {self.lastnames} - ({self.document_id})"
