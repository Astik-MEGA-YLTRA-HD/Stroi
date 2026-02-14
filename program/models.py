from django.db import models

class Orders(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    deadline = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    remains = models.DecimalField(max_digits=20, decimal_places=2)

class Day(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)

class Сonsumables(models.Model):
    title = models.CharField(max_length=255)
    count = models.DecimalField(max_digits=20, decimal_places=2)
    prise = models.DecimalField(max_digits=20, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)