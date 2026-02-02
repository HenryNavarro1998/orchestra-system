from django.db import models
from django.core.exceptions import ValidationError


class MusicalProgram(models.Model):

    name = models.CharField(max_length=70, default="Programa Académico Orquestal")

    def __str__(self):
        return f"{self.name}"
