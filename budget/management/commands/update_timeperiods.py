from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from budget.models import TimePeriod, Category, CurrentTimePeriod
from datetime import timedelta
from calendar import monthrange

class Command(BaseCommand):
    help = 'Update time periods and create new categories'

    def handle(self, *args, **kwargs):
        now = timezone.now().astimezone(timezone.get_current_timezone())  # Current time in Chicago timezone
        now_epoch = int(now.timestamp())
        users = User.objects.all()

        for user in users:
            # Init time periods for user
            self.initialize_time_periods(now, user)

            # Get most up-to-date time period
            latest_time_period = TimePeriod.objects.filter(user=user).order_by('-index').first()

            # TODO: Make this work with day, month, and year
            # TODO: Update check if latest is not current
            if latest_time_period:
                new_index = latest_time_period.index + 1

                if latest_time_period.type == 'day':
                    new_index = latest_time_period.index + timedelta(days=1).total_seconds()
                elif latest_time_period.type == 'week':
                    new_index = latest_time_period.index + timedelta(weeks=1).total_seconds()
                elif latest_time_period.type == 'month':
                    next_month = (timezone.datetime.fromtimestamp(latest_time_period.index).replace(day=28) + timedelta(days=4)).replace(day=1)
                    new_index = int(next_month.timestamp())
                elif latest_time_period.type == 'year':
                    next_year = timezone.datetime.fromtimestamp(latest_time_period.index).replace(year=timezone.datetime.fromtimestamp(latest_time_period.index).year + 1, month=1, day=1)
                    new_index = int(next_year.timestamp())
                else:
                    continue

                new_time_period = TimePeriod.objects.create(
                    user=user,
                    type=latest_time_period.type,
                    index=int(new_index)
                )

                # Copy categories from the previous time period
                categories = Category.objects.filter(user=user, timeperiod=latest_time_period)
                for category in categories:
                    Category.objects.create(
                        user=user,
                        timeperiod=new_time_period,
                        category=category.category,
                        amount=category.amount
                    )

                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period} for user {user}'))
            else:
                self.initialize_time_periods(now, user)
    def time_period_exists(self, user, period_type):
        return TimePeriod.objects.filter(user=user, type=period_type).exists()

    def initialize_time_periods(self, now, user):

        days_since_sunday = (now.weekday() + 1) % 7  # Monday is 0, Sunday is 6
        start_of_previous_sunday = now - timedelta(days=days_since_sunday)
        start_of_previous_sunday = start_of_previous_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        new_week_index = int(start_of_previous_sunday.timestamp())

        beginning_of_month = now.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        beginning_of_year = now.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        if not self.time_period_exists(user, "week"):
            # Create an initial time period for the user
            initial_time_period_week = TimePeriod.objects.create(
                user=user,
                type='week',  # Default period type
                index=new_week_index
            )

            curr_time_period = CurrentTimePeriod.objects.create(
                user=user,
                period=initial_time_period_week
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_week} for user {user}'))

        if not self.time_period_exists(user, "month"):
            initial_time_period_month = TimePeriod.objects.create(
                user=user,
                type='month',  # Default period type
                index=int(beginning_of_month.timestamp())
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_month} for user {user}'))

        if not self.time_period_exists(user, "year"):
            initial_time_period_year = TimePeriod.objects.create(
                user=user,
                type='year',  # Default period type
                index=int(beginning_of_year.timestamp())
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_year} for user {user}'))





