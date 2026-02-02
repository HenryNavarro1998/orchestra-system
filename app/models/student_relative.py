from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
import re

DOCUMENT_TYPE_CHOICES = [
    ('V', 'Venezolano/a'),
    ('E', 'Extranjero/a'),
]

GENDER_CHOICES = [
    ('Femenine', 'Femenino'),
    ('Masculine', 'Masculino'),
]


class StudentRelative(models.Model):

    MARITAL_STATUS_CHOICES = [
        ('Single', 'Soltero/a'),
        ('Married', 'Casado/a'),
        ('Divorced', 'Divorciado/a'),
        ('Widowed', 'Viudo/a'),
        ('Concubinage', 'Concubinato'),
        ('Stable union', 'Unión estable')
    ]

    ############ DATOS DEL REPRESENTANTE LEGAL

    relationship = models.CharField(
        max_length=20,
        null=True,
        help_text="Parentesco del representante legal."
    )

    fullname =  models.CharField(
        max_length=70,
        null=True,
        help_text="Nombre completo del representante legal."
    )

    born_date = models.DateField(
        help_text="Fecha de nacimiento del representante legal",
        null=True,
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        null=True,
        help_text="Estado civil del representante legal.",
    )
    document_id = models.CharField(
        max_length=8,
        null=True,
        help_text="Cédula o Pasaporte del representante legal.",
    )
    nationality = models.CharField(
        max_length=1,
        choices=DOCUMENT_TYPE_CHOICES,
        null=True,
        help_text="Nacionalidad del representante legal.",
    )
    profession = models.CharField(
        max_length=30,
        null=True,
        help_text="Profesión u oficio del representante legal."
    )
    address= models.TextField(
        max_length=300,
        blank=True,  
        null=True,
        help_text="Dirección de Habitación (Solo si es diferente a la del Beneficiario)."
    )
    home_phone = models.CharField(
        max_length=11,
        blank=True,  # Permite que el campo esté en blanco en el formulario
        null=True,   
        help_text="Número de Habitación (Solo si es diferente a la del Beneficiario)."
    )
    cellphone = models.CharField(
        max_length=11,
        null=True,
        help_text="Número de teléfono celular."
    )
    email = models.EmailField(
        max_length=50,
        null=True,
        help_text="Correo electrónico del representante legal."
    )
    workplace = models.CharField(
        max_length=40,
        blank=True,  
        null=True,
        help_text="Lugar de trabajo del representante legal."
    )
    job_title = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Cargo del representante legal."
    )    
    office_phone = models.CharField(
        max_length=11,
        blank=True,  
        null=True,   
        help_text="Número de Oficina."
    )

    class Meta:
        verbose_name = "Familiar"
        verbose_name_plural = "Familiares"

    def clean(self):
        super().clean()

        # Validación para born_date:
        if self.born_date: 
            today = timezone.now().date()
            min_born_date = today.replace(year=today.year - 18)  # Aproximación de 18 años
            if self.born_date and self.born_date > min_born_date:
                raise ValidationError({'born_date': 'El representante debe tener más de 18 años.'})
            
        # Validación para datos del representante legal
        if self.document_id: 
            if not (7 <= len(self.document_id) <= 8):
                raise ValidationError({'document_id': 'El ID del documento debe tener entre 7 y 8 caracteres.'})
            
            # Lógica de validación de born_date vs document_id para registros existentes
            if self.document_id and self.born_date:
                # Excluye la instancia actual si ya existe (para actualizaciones)
                queryset = StudentRelative.objects.filter(document_id=self.document_id)
                if self.pk: # Si es una instancia existente
                    queryset = queryset.exclude(pk=self.pk)

                existing_record_with_same_id = queryset.first()

                if existing_record_with_same_id and existing_record_with_same_id.born_date != self.born_date:
                    raise ValidationError({
                        'document_id': 'Esta cédula está registrada para una persona diferente.'
                    })

        if self.home_phone: # Check if the field has a value before applying regex
            if self.home_phone and not re.fullmatch(r'^\d{11}$', self.home_phone):
                raise ValidationError({'home_phone': 'El número de teléfono de casa debe ser una cadena de 11 dígitos numéricos.'})
            
        if self.cellphone: # Check if the field has a value before applying regex
            if self.cellphone and not re.fullmatch(r'^\d{11}$', self.cellphone):
                raise ValidationError({'cellphone': 'El número de celular debe ser una cadena de 11 dígitos numéricos.'})
            
        if self.office_phone: # Check if the field has a value before applying regex
            if self.office_phone and not re.fullmatch(r'^\d{11}$', self.office_phone):
                raise ValidationError({'office_phone': 'El número de oficina debe ser una cadena de 11 dígitos numéricos.'})

            
    def __str__(self):
        return f"{self.fullname} ({self.document_id})"