import datetime
from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import time


def latest_time_period_by_type(user, type):
    return TimePeriod.objects.filter(user=user, type=type).order_by('ordering').first()


def time_period_type_exists(user, period_type):
    return TimePeriod.objects.filter(user=user, type=period_type).exists()


def current_time_index_exists(user, index):
    time_p = TimePeriod.objects.filter(user=user, index=index).first()
    out = CurrentTimePeriod.objects.filter(user=user, period=time_p).exists()
    print("Time period: " + str(time_p))
    print("Current Time exists:" + str(out))
    return out


def time_period_index_exists(user, index):
    out = TimePeriod.objects.filter(user=user, index=index).exists()
    print(user)
    print("Time Period Index Exists" + str(out))
    return out


def copy_categories(user, prev, new):
    categories = Category.objects.filter(user=user, timeperiod=prev)
    for category in categories:
        Category.objects.create(
            user=user,
            timeperiod=new,
            category=category.category,
            amount=category.amount
        )


def initialize_time_periods(now, user):
    days_since_sunday = (now.weekday() + 1) % 7  # Monday is 0, Sunday is 6
    start_of_previous_sunday = now - timedelta(days=days_since_sunday)
    start_of_previous_sunday = start_of_previous_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    new_week_index = int(start_of_previous_sunday.timestamp())

    first_day_of_month = datetime.datetime(now.year, now.month, 1, 0, 0).timestamp()
    first_day_of_year = datetime.datetime(now.year, 1, 1, 0, 0).timestamp()

    if not time_period_index_exists(user, new_week_index):
        # Create an initial time period for the user
        initial_time_period_week = TimePeriod.objects.create(
            user=user,
            type='week',  # Default period type
            index=new_week_index
        )

        latest_week = latest_time_period_by_type(user, "week")
        copy_categories(user, latest_week, initial_time_period_week)

        curr_time_period = CurrentTimePeriod.objects.create(
            user=user,
            period=initial_time_period_week
        )

    if not time_period_index_exists(user, first_day_of_month):
        # Create an initial time period for the user
        initial_time_period_month = TimePeriod.objects.create(
            user=user,
            type='month',  # Default period type
            index=first_day_of_month
        )

        latest_month = latest_time_period_by_type(user, "month")
        copy_categories(user, latest_month, initial_time_period_month)

    if not time_period_index_exists(user, first_day_of_year):
        # Create an initial time period for the user
        initial_time_period_year = TimePeriod.objects.create(
            user=user,
            type='year',  # Default period type
            index=first_day_of_year
        )

        latest_year = latest_time_period_by_type(user, "month")
        copy_categories(user, latest_year, initial_time_period_year)


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
