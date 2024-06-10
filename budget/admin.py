from django.contrib import admin
from .models import TimePeriod, Category, Payment, CurrentTimePeriod


class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'index')
    list_filter = ('type', 'user')
    search_fields = ('user__username', 'type')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'timeperiod', 'category', 'amount')
    list_filter = ('user', 'timeperiod', 'category')
    search_fields = ('user__username', 'category')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'budget', 'date', 'amount', 'description')
    list_filter = ('user', 'budget', 'date')
    search_fields = ('user__username', 'budget__category', 'description')


class CurrentPeriod(admin.ModelAdmin):
    list_display = ('user', 'period', 'id')
    list_filter = ('user', 'period')
    search_fields = ('user__username', 'period')

admin.site.register(TimePeriod, TimePeriodAdmin)
admin.site.register(CurrentTimePeriod, CurrentPeriod)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Payment, PaymentAdmin)

