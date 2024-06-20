import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from budget import models
from budget.models import TimePeriod, Category, CurrentTimePeriod


def is_in_current_period(prev, fut):
    now = int(timezone.now().timestamp())
    output = now in range(int(prev), int(fut))
    return output


class Command(BaseCommand):
    help = 'Update time periods and create new categories'

    def handle(self, *args, **kwargs):
        now = timezone.now().astimezone(timezone.get_current_timezone())  # Current time in Chicago timezone
        users = User.objects.all()

        for user in users:
            models.initialize_time_periods(now, user)
            # Get most up-to-date time period
            latest_week = models.latest_time_period_by_type(user, "week")
            latest_month = models.latest_time_period_by_type(user, "month")
            latest_year = models.latest_time_period_by_type(user, "year")

            # Week
            new_index_week = latest_week.get_next_period_index()
            print(latest_week)
            print(new_index_week)
            if not is_in_current_period(latest_week.index, new_index_week) and not models.time_period_index_exists(user, int(new_index_week)):
                new_time_period_week = TimePeriod.objects.create(
                    user=user,
                    type="week",
                    index=int(new_index_week)
                )
                models.copy_categories(user, latest_week, new_time_period_week)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_week} for user {user}'))

            # Month
            new_index_month = latest_month.get_next_period_index()
            if not is_in_current_period(latest_month.index, new_index_month) and not models.time_period_index_exists(user, new_index_month):
                new_time_period_month = TimePeriod.objects.create(
                    user=user,
                    type="month",
                    index=int(new_index_month)
                )
                models.copy_categories(user, latest_month, new_time_period_month)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_month} for user {user}'))

            # Year
            new_index_year = latest_year.get_next_period_index()
            if not is_in_current_period(latest_year.index, new_index_year) and not models.time_period_index_exists(user, new_index_year):
                new_time_period_year = TimePeriod.objects.create(
                    user=user,
                    type="year",
                    index=int(new_index_year)
                )
                models.copy_categories(user, latest_year, new_time_period_year)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_index_year} for user {user}'))

