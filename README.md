This is a website designed to help you keep track of your budget on a weekly/monthly/yearly basis.

## Supported OS
Linux

## Requierments/Preesiquites
```
Python ---------- 3.10
Django ---------- 5.0.2
django-crontab -- 0.7.1
```

### Setup
Clone the project onto your local device using
```
git clone https://github.com/Mechanist0/budget_tracker.git
```

Open the project using your IDE of choice

Open the command line and run the following commands
```
python manage.py makemigrations
python manage.py migrate
```
Then run the following command and follow the instructions
```
python manage.py createsuperuser
```
Then create the initial time periods with this command
```
python manage.py update_timeperiods
```

Finally, run the app
```
python3 manage.py runserver
```
