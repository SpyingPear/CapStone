from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Publisher, Article, Newsletter

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Role & Subscriptions', {
            'fields': ('role', 'subscriptions_publishers', 'subscriptions_journalists',
                       'articles_independent', 'newsletters_independent')
        }),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('editors', 'journalists')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher')
    search_fields = ('title', 'content')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'created_at')
    list_filter = ('publisher',)
    search_fields = ('title', 'content')
