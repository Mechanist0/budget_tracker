from django.db import models
from django.db.models import Sum
from django.urls import reverse  # Used in get_absolute_url() to get URL for specified ID

from django.db.models import UniqueConstraint  # Constrains fields to unique values
from django.db.models.functions import Lower  # Returns lower cased value of field
from django.contrib.auth.models import User
import time


class TimePeriod(models.Model):
    """Model representing time periods for all categories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=200)  # Time period type, can be day/week/month/year
    index = models.IntegerField()  # Epoch timestamp as index

    def convert_to_human_readable(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(self.index))
    def __str__(self):
        return f"{self.type} starting at {self.convert_to_human_readable()} for {self.user}"


class CurrentTimePeriod(models.Model):
    """Model representing current time periods for all categories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period = models.ForeignKey(TimePeriod, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.period}"

class Category(models.Model):
    """Model representing a budget Category"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    timeperiod = models.ForeignKey(TimePeriod, on_delete=models.CASCADE, default=None)
    category = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_total(self):
        return "Lmaos"

    def __str__(self):
        """String for representing the Model object."""
        return self.category

    def get_absolute_url(self):
        """Returns the URL to access a detail record for the budget."""
        return reverse('budget-detail', args=[str(self.id)])


class Payment(models.Model):
    """Model representing a specific payment to a category."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.amount} on {self.date}"

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this payment."""
        return reverse('payment-detail', args=[str(self.id)])
