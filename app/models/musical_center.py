from django.db import models


class MusicalCenter(models.Model):
    TYPE_CHOICES = [
        ('academic_center', 'Centro Académico'),
        ('center',          'Núcleo'),
        ('extension',       'Extensión'),
        ('module',          'Módulo'),
        ('management',      'Gerencia'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    code = models.CharField(max_length=100, default=0)
    bathrooms_quantity = models.PositiveIntegerField(default=0, null=True)
    wc_quantity = models.PositiveIntegerField(default=0, null=True)
    municipality = models.CharField(max_length=70, blank=True)
    parish = models.CharField(max_length=70, blank=True)
    address = models.CharField(max_length=200, blank=True)
    director_name = models.CharField(max_length=70, blank=True)


    class Meta:
        verbose_name = "Núcleo"
        verbose_name_plural = "Núcleos"
        ordering = ["name"]


    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"