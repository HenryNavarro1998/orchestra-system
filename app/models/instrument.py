from django.db import models

class Instrument(models.Model):

    CATEGORY_CHOICES = [
        ('Wind','Viento'),
        ('String','Cuerdas'),
        ('Percussion','Percusión'),
        ('Other','Otros'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"