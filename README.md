# Budget Tracker
This is a website designed to help you keep track of your budget on a weekly/monthly/yearly basis.

---

### Supported OS
Linux

---

### TODO
- [ ] Encrypt database using Post-Quantum Cryptography
- [ ] Implement test suite
- [ ] Fix graph page

---

### Requirements
```
Python ---------- 3.10
Django ---------- 5.0.2
django-crontab -- 0.7.1
```

---

### Setup
Clone the project onto your local device using
```
git clone https://github.com/Mechanist0/budget_tracker.git
```

Open the project using your IDE of choice

Open the command line and run the following commands
- makemigrations will make migrations based on the files in [Migrations](https://github.com/Mechanist0/budget_tracker/tree/main/budget/migrations)
- migrate will apply the migrations to the database
```
python manage.py makemigrations
python manage.py migrate
```
Then run the following command and follow the instructions to create your superuser
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

---

### Use
Once you have logged in, pick your period by selecting it from the drop-down in the Time Period tab, 
this lets you specify if you are working on a weekly/monthly/yearly basis.

Then you can create a new category to track a specified budget. 
All categories will be copied over automatically at the start of the next week. (Sunday at 00:00 America\Chicago)