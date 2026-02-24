from django.contrib import admin
from app_reviews.models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'product', 'date_posted', 'rating' )
    search_fields = ('ozon_id', )

admin.site.register(Review, ReviewAdmin)