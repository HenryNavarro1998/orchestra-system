from django.db import models
from django.core.exceptions import ValidationError

class AcademicPeriod(models.Model):
    first_year = models.PositiveIntegerField()
    final_year = models.PositiveIntegerField()
    is_active  = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Período Académico"
        verbose_name_plural = "Períodos Académicos"
        ordering = ["-first_year"]

    def clean(self):
        if self.final_year != self.first_year + 1:
            raise ValidationError("El año final debe ser exactamente un año mayor que el año inicial.")


    def __str__(self):
        return f"{self.first_year}-{self.final_year}"


    def clean(self):
        if self.is_active:
            active_exists = AcademicPeriod.objects.filter(is_active=True).exclude(pk=self.pk).exists()
            if active_exists:
                raise ValidationError("Ya existe un Período Escolar activo. Solo uno puede estar activo a la vez.")