from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from app.models import StudentRelative
import re

DOCUMENT_TYPE_CHOICES = [
    ('V', 'Venezolano/a'),
    ('E', 'Extranjero/a'),
]

GENDER_CHOICES = [
    ('Femenine', 'Femenino'),
    ('Masculine', 'Masculino'),
]

class Student(models.Model):

    ############ Datos personales del BENEFICIARIO

    # lógica del DNI: Si tiene, debe ser única. Si no tiene, debe tener valor N/A.
    document_id = models.CharField(
        max_length=8,
        blank=True,
        help_text="Cédula o Pasaporte del estudiante."
    )

    has_document_id = models.BooleanField(
        default=True,
        help_text="Marque si el estudiante posee cédula o pasaporte."    )

    
    id_legal_parent = models.ForeignKey(
        StudentRelative, 
        on_delete=models.CASCADE, 
        related_name='student_legal_parent',
        null=True,
    )

    id_relative = models.ForeignKey(
        StudentRelative, 
        on_delete=models.CASCADE, 
        related_name='student_relative',
        null=True,
    )

    nationality = models.CharField(
        max_length=1,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text="Nacionalidad del estudiante ('V' para Venezolano, 'E' para Extranjero)."
    )

    names = models.CharField(
        max_length=30,
        help_text="Nombres del estudiante."
    )
    lastnames = models.CharField(
        max_length=30,
        help_text="Apellidos del estudiante."
    )
    born_date = models.DateField(
        help_text="Fecha de nacimiento del estudiante (debe tener más de 5 años)."
    )
    gender = models.CharField(
        max_length=10, 
        choices=GENDER_CHOICES,
        help_text="Género del estudiante."
    )
    address = models.TextField(
        max_length=300,
        help_text="Dirección del estudiante (máximo 300 caracteres).",
        null=True,
    )
    home_phone = models.CharField(
        max_length=11,
        blank=True,  # Permite que el campo esté en blanco en el formulario
        null=True,   # Permite que el campo sea NULL en la base de datos
        help_text="Número de teléfono de casa."
    )
    cellphone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        help_text="Número de teléfono celular."
    )
    email = models.EmailField(
        max_length=50,
        null=True,
        help_text="Correo electrónico del estudiante."
    )
    cellphone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        help_text="Número de teléfono celular."
    )

    ############ Datos Académicos DEL BENEFICIARIO
    academic_institution_name = models.CharField(
        max_length=70,
        null=True,
        help_text="Nombre del Plantel Educativo."
    )
    academic_institution_address = models.TextField(
        max_length=200,
        null=True,
        help_text="Dirección del Plantel Educativo."
    )
    academic_degree = models.CharField(
        max_length=30,
        null=True,
        help_text="Grado académico."
    )
    academic_institution_type = models.CharField(
        max_length=30,
        null=True,
        help_text="Tipo de Plantel (Privado, Mixto, etc.)"
    )

    ############ PÚBLICO
    housing_type = models.CharField(
        max_length=30,
        null=True,
        help_text="Tipo de Vivienda (Casa, Edificio, Apartamento, Quinta, etc.)"
    )
    housing_condition = models.CharField(
        max_length=30,
        null=True,
        help_text="Estado de la Vivienda (Propia, Alquilada, etc.)"
    )
    number_people_living_housing = models.IntegerField(
        default=1,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Cantidad de personas que habitan en la Vivienda."
    )

    ############ DATOS MÉDICOS DEL BENEFICIARIO    
    allergies = models.TextField(
        max_length=150,
        null=True,
        blank=True,  
        help_text="Indique las alergias del estudiante. Dejar en blanco si no tiene o se desconocen."
    )
    regular_medical_treatment = models.TextField(
        max_length=200,
        null=True,
        blank=True, 
        help_text="Indique si el estudiante toma tratamiento médico regular. Dejar en blanco en caso contrario."
    )
    medical_report = models.TextField(
        max_length=200,
        null=True,
        blank=True, 
        help_text="Indique datos del informe médico del estudiante. Dejar en blanco en caso contrario."
    )


    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def clean(self):
        super().clean()

        # Validación para document_id:
        if self.document_id: 
            if not (3 <= len(self.document_id) <= 8):
                raise ValidationError({'document_id': 'El ID del documento debe tener entre 3 y 8 caracteres.'})

        # Validación para born_date:
        if self.born_date: 
            today = timezone.now().date()
            min_born_date = today - timezone.timedelta(days=5 * 365.25)  # Aproximación de 5 años
            if self.born_date and self.born_date > min_born_date:
                raise ValidationError({'born_date': 'El estudiante debe tener más de 5 años.'})

        # Validación para home_phone y cellphone (si no son nulos):
        if self.home_phone: # Check if the field has a value before applying regex
            if self.home_phone and not re.fullmatch(r'^\d{11}$', self.home_phone):
                raise ValidationError({'home_phone': 'El número de teléfono de casa debe ser una cadena de 11 dígitos numéricos.'})
        if self.cellphone: # Check if the field has a value before applying regex
            if self.cellphone and not re.fullmatch(r'^\d{11}$', self.cellphone):
                raise ValidationError({'cellphone': 'El número de celular debe ser una cadena de 11 dígitos numéricos.'})

        # Validación para id_legal_parent y id_relative (desde backend, pero también se maneja desde el formulario)
        if self.id_legal_parent and self.id_relative:
            if self.id_legal_parent == self.id_relative:
                raise ValidationError(
                    {'id_relative': 'El representante legal y el pariente no pueden ser la misma persona.'}
                )    
            
    def __str__(self):
        return f"{self.names} {self.lastnames} ({self.document_id})"