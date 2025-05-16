from django.contrib import admin
from .models import ServerResponse

class SeverResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'name', 'time' )
    #search_fields = ('article', )



admin.site.register(ServerResponse, SeverResponseAdmin)
