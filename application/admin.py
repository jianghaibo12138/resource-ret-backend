from django.contrib import admin

# Register your models here.

from application.models import Order, AuthUser


class AuthUserAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    pass


admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(Order, OrderAdmin)
