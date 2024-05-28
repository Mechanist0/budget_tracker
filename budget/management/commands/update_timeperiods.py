from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from budget.models import TimePeriod, Category, CurrentTimePeriod
from datetime import timedelta


def latest_time_period_by_type(user, type):
    return TimePeriod.objects.filter(user=user, type=type).order_by('-ordering').first()


def time_period_exists(user, period_type):
    return TimePeriod.objects.filter(user=user, type=period_type).exists()


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
    print(f'{prev} < {now} < {fut}')
    return prev <= now <= fut


class Command(BaseCommand):
    help = 'Update time periods and create new categories'

    def handle(self, *args, **kwargs):
        now = timezone.now().astimezone(timezone.get_current_timezone())  # Current time in Chicago timezone
        now_epoch = int(now.timestamp())
        users = User.objects.all()

        for user in users:
            # Get most up-to-date time period
            latest_week = latest_time_period_by_type(user, "week")
            latest_month = latest_time_period_by_type(user, "month")
            latest_year = latest_time_period_by_type(user, "year")

            if not latest_week and latest_month and latest_year:
                # Week
                new_index_week = latest_week.index + timedelta(weeks=1).total_seconds()
                if is_in_current_period(latest_week.index, new_index_week) and not latest_week:
                    new_time_period_week = TimePeriod.objects.create(
                        user=user,
                        type="week",
                        index=int(new_index_week)
                    )
                    copy_categories(user, latest_week, new_time_period_week)
                    self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_week} for user {user}'))

                # Month
                next_month = (timezone.datetime.fromtimestamp(latest_month.index).replace(day=28) + timedelta(days=4)).replace(day=1)
                new_index_month = int(next_month.timestamp())
                if is_in_current_period(latest_month.index, new_index_month) and not latest_month:
                    new_time_period_month = TimePeriod.objects.create(
                        user=user,
                        type="month",
                        index=int(new_index_month)
                    )
                    copy_categories(user, latest_month, new_time_period_month)
                    self.stdout.write(self.style.SUCCESS(f'Created new time period {new_time_period_month} for user {user}'))

                # Year
                next_year = timezone.datetime.fromtimestamp(latest_year.index).replace(year=timezone.datetime.fromtimestamp(latest_year.index).year + 1, month=1, day=1)
                new_index_year = int(next_year.timestamp())
                if is_in_current_period(latest_year.index, new_index_year) and not latest_year:
                    new_time_period_year = TimePeriod.objects.create(
                        user=user,
                        type="year",
                        index=int(new_index_year)
                    )
                    copy_categories(user, latest_year, new_time_period_year)
                    self.stdout.write(self.style.SUCCESS(f'Created new time period {new_index_year} for user {user}'))
            else:
                self.initialize_time_periods(now, user)

    def initialize_time_periods(self, now, user):
        days_since_sunday = (now.weekday() + 1) % 7  # Monday is 0, Sunday is 6
        start_of_previous_sunday = now - timedelta(days=days_since_sunday)
        start_of_previous_sunday = start_of_previous_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        new_week_index = int(start_of_previous_sunday.timestamp())

        beginning_of_month = now.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        beginning_of_year = now.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        if not time_period_exists(user, "week"):
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

        if not time_period_exists(user, "month"):
            initial_time_period_month = TimePeriod.objects.create(
                user=user,
                type='month',  # Default period type
                index=int(beginning_of_month.timestamp())
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_month} for user {user}'))

        if not time_period_exists(user, "year"):
            initial_time_period_year = TimePeriod.objects.create(
                user=user,
                type='year',  # Default period type
                index=int(beginning_of_year.timestamp())
            )
            self.stdout.write(self.style.SUCCESS(f'Created initial time period {initial_time_period_year} for user {user}'))





