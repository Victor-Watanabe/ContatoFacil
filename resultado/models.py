from django.db import models

# Criar o Local
class locai(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(max_length=1000)
    email_address = models.CharField(max_length=100)
    number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

