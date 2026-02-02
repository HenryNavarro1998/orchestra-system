from django.db import models

class AdminCollateral(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Colateral"
        verbose_name_plural = "Colateral"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.code}]"
