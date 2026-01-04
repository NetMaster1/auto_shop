from django.contrib import admin
from . models import ExtendedUser

class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email_confirm_code', )


admin.site.register(ExtendedUser, ExtendedUserAdmin)

