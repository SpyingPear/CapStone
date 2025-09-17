from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='editor_publishers', blank=True)
    journalists = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='journalist_publishers', blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Roles(models.TextChoices):
        READER = 'READER', 'Reader'
        EDITOR = 'EDITOR', 'Editor'
        JOURNALIST = 'JOURNALIST', 'Journalist'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.READER)

    # Reader-specific fields (subscriptions)
    subscriptions_publishers = models.ManyToManyField(Publisher, related_name='subscribed_readers', blank=True)
    subscriptions_journalists = models.ManyToManyField('self',
                                                       symmetrical=False,
                                                       related_name='reader_subscribers',
                                                       blank=True,
                                                       limit_choices_to={'role': Roles.JOURNALIST})

    # Journalist-specific fields (independent publications)
    # These are maintained by signals based on Article/Newsletter publisher=None
    articles_independent = models.ManyToManyField('Article', related_name='independent_by', blank=True)
    newsletters_independent = models.ManyToManyField('Newsletter', related_name='independent_by', blank=True)

    def clean(self):
        # Enforce "None" (cleared) for the opposite role fields
        # Note: ManyToMany can't be None, so we ensure they are empty on save.
        pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Ensure group assignment matches role
        try:
            if self.role == self.Roles.READER:
                reader_group, _ = Group.objects.get_or_create(name='Reader')
                self.groups.set([reader_group])
                # Clear journalist-only fields
                self.articles_independent.clear()
                self.newsletters_independent.clear()
            elif self.role == self.Roles.EDITOR:
                editor_group, _ = Group.objects.get_or_create(name='Editor')
                self.groups.set([editor_group])
                # Clear reader/journalist-only relation fields that shouldn't apply
                # (Editors can be kept neutral; do not force-clear subscriptions)
            elif self.role == self.Roles.JOURNALIST:
                journalist_group, _ = Group.objects.get_or_create(name='Journalist')
                self.groups.set([journalist_group])
                # Clear reader-only fields
                self.subscriptions_publishers.clear()
                self.subscriptions_journalists.clear()
        except Exception:
            # During initial migrations/groups missing: ignore
            pass

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_independent(self):
        return self.publisher is None

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='newsletters')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='newsletters')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_independent(self):
        return self.publisher is None
