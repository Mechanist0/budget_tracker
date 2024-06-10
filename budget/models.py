from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import time


class TimePeriodManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        desired_order = ['week', 'month', 'year']
        ordering = models.Case(
            *[models.When(type=type_value, then=models.Value(index)) for index, type_value in enumerate(desired_order)],
            default=len(desired_order),
            output_field=models.IntegerField(),
        )
        return queryset.annotate(ordering=ordering).order_by('ordering')


class TimePeriod(models.Model):
    """Model representing time periods for all categories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=200)  # Time period type, can be day/week/month/year
    index = models.IntegerField()  # Epoch timestamp as index

    objects = TimePeriodManager()

    """Is the index in current period range"""
    def is_in_timeperiod(self, period):
        if type(period) is CurrentTimePeriod:
            return period.period.index in range(self.index, int(self.get_next_period_index()))
        return period.index in range(self.index, self.get_next_period_index())

    def get_next_period_index(self):
        match self.type:
            case 'week':
                return self.index + timedelta(weeks=1).total_seconds()
            case 'month':
                next_month = (timezone.datetime.fromtimestamp(self.index).replace(day=28) + timedelta(days=4)).replace(day=1)
                return int(next_month.timestamp())
            case 'year':
                next_year = timezone.datetime.fromtimestamp(self.index).replace(year=timezone.datetime.fromtimestamp(self.index).year + 1, month=1, day=1)
                return int(next_year.timestamp())

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
