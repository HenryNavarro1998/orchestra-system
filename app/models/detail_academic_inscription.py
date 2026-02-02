from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class DetailAcademicInscription(models.Model):
    TYPE_CHOICES = [
        ('New admission', 'Nuevo ingreso'),
        ('Re-entry', 'Reingreso'),
        ('Data update', 'Actualización de datos'),
        ('Re-enrollment', 'Reinscripción regular'),
    ]

    id_student = models.ForeignKey('app.Student', on_delete=models.CASCADE)
    id_orchestral_project = models.ForeignKey('app.OrchestralProject',  null=True, on_delete=models.CASCADE)
    id_musical_program = models.ForeignKey('app.MusicalProgram', on_delete=models.CASCADE)
    id_musical_center = models.ForeignKey('app.MusicalCenter', null=True, on_delete=models.CASCADE)
    id_instrument = models.ForeignKey('app.Instrument', on_delete=models.CASCADE)
    id_academic_period = models.ForeignKey('app.AcademicPeriod', on_delete=models.CASCADE)
    inscription_date = models.DateField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)


    class Meta:
        verbose_name = "Detalle de Inscripción Académica"
        verbose_name_plural = "Detalles de Inscripción Académica"
        #unique_together es porque un estudiante no puede estar inscrito 2 veces en el mismo período académico 
        unique_together = ('id_student', 'id_academic_period')
        ordering = ['id_academic_period']


    def clean(self):
        super().clean()
        
        # Validación: fecha no puede ser futura
        if self.inscription_date and self.inscription_date > timezone.now().date():
            raise ValidationError({'inscription_date': 'La inscripción no puede ser futura y debe ser una fecha válida.'})
        
        # Validación: tipo debe estar en las opciones (redundante si usas choices)
        if self.type not in dict(self.TYPE_CHOICES):
            raise ValidationError({'type': 'Tipo de inscripción inválido.'})


    def __str__(self):
        return f"{self.id_student} - {self.id_academic_period} ({self.type})"

