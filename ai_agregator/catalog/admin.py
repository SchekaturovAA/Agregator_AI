from django.contrib import admin

from django.contrib import admin

from .models import Category, Tag, AIService, Feature, PricingPlan, Bookmark
from .models import AIService
from django.utils.safestring import mark_safe


@admin.register(AIService)
class AIServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_model', 'rating', 'is_verified', 'is_active']
    list_filter = ['category', 'price_model', 'is_verified', 'is_active']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = [
        (None, {
            'fields': ['name', 'slug', 'category', 'tags']
        }),
        ('Описание', {
            'fields': ['short_description', 'full_description', 'logo']  # добавили logo
        }),
        ('Детали', {
            'fields': ['url', 'price_model', 'price_description', 'rating', 'review_count']
        }),
        ('Статус', {
            'fields': ['is_verified', 'is_active']
        }),
    ]

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="50" height="50" />')
        return "Нет логотипа"

    logo_preview.short_description = 'Превью логотипа'

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Feature)
admin.site.register(PricingPlan)


from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'city']
    list_filter = ['country', 'city']
    search_fields = ['user__username', 'user__email', 'country', 'city']

from django.contrib import admin
from .models import Bookmark



@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'service__name']

from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__username', 'service__name']

