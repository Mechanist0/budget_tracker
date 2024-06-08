from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from budget.models import TimePeriod, Category, CurrentTimePeriod
from datetime import timedelta


def latest_time_period_by_type(user, type):
    return TimePeriod.objects.filter(user=user, type=type).order_by('ordering').first()


def time_period_type_exists(user, period_type):
    return TimePeriod.objects.filter(user=user, type=period_type).exists()


def current_time_index_exists(user, index):
    time_p = TimePeriod.objects.filter(user=user, index=index).first()
    print(time_p)
    out = CurrentTimePeriod.objects.filter(user=user, period=time_p).exists()
    print(out)
    return out


def time_period_index_exists(user, index):
    out = TimePeriod.objects.filter(user=user, index=index).exists()
    print(out)
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


def is_in_current_period(prev, fut):
    now = int(timezone.now().timestamp())
    output = now in range(int(prev), int(fut))
    print(f'prev {prev} < now {now} < future {fut} = {output}')
    return output


class Command(BaseCommand):
    help = 'Update time periods and create new categories'

    def handle(self, *args, **kwargs):
        now = timezone.now().astimezone(timezone.get_current_timezone())  # Current time in Chicago timezone
        users = User.objects.all()

        for user in users:
            self.initialize_time_periods(now, user)
            # Get most up-to-date time period
            latest_week = latest_time_period_by_type(user, "week")
            latest_month = latest_time_period_by_type(user, "month")
            latest_year = latest_time_period_by_type(user, "year")

            # Week
            new_index_week = latest_week.get_next_period_index()
            if not is_in_current_period(latest_week.index, new_index_week) and not time_period_index_exists(user, new_index_week):
                new_time_period_week = TimePeriod.objects.create(
                    user=user,
                    type="week",
                    index=int(new_index_week)
                )
                copy_categories(user, latest_week, new_time_period_week)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_week} for user {user}'))

            # Month
            new_index_month = latest_month.get_next_period_index()
            if not is_in_current_period(latest_month.index, new_index_month) and not time_period_index_exists(user, new_index_month):
                new_time_period_month = TimePeriod.objects.create(
                    user=user,
                    type="month",
                    index=int(new_index_month)
                )
                copy_categories(user, latest_month, new_time_period_month)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_month} for user {user}'))

            # Year
            new_index_year = latest_year.get_next_period_index()
            if not is_in_current_period(latest_year.index, new_index_year) and not time_period_index_exists(user, new_index_year):
                new_time_period_year = TimePeriod.objects.create(
                    user=user,
                    type="year",
                    index=int(new_index_year)
                )
                copy_categories(user, latest_year, new_time_period_year)
                self.stdout.write(self.style.SUCCESS(f'Created new time period {new_index_year} for user {user}'))

    def initialize_time_periods(self, now, user):
        latest_week = latest_time_period_by_type(user, "week")
        days_since_sunday = (now.weekday() + 1) % 7  # Monday is 0, Sunday is 6
        start_of_previous_sunday = now - timedelta(days=days_since_sunday)
        start_of_previous_sunday = start_of_previous_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        new_week_index = int(start_of_previous_sunday.timestamp())

        if not current_time_index_exists(user, new_week_index):
            # Create an initial time period for the user
            initial_time_period_week = TimePeriod.objects.create(
                user=user,
                type='week',  # Default period type
                index=new_week_index
            )
            copy_categories(user, latest_week, initial_time_period_week)

            curr_time_period = CurrentTimePeriod.objects.create(
                user=user,
                period=initial_time_period_week
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_week} for user {user}'))