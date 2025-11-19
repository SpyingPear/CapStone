import logging
import requests
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models.signals import post_migrate, pre_save, post_save
from django.dispatch import receiver

from .models import Article, Newsletter, User, Publisher

logger = logging.getLogger(__name__)


def _ensure_groups_and_permissions():
    """
    Create the required groups and assign CRUD permissions per the brief.

    - Reader: view article/newsletter
    - Editor: view, change, delete article/newsletter
    - Journalist: add, view, change, delete article/newsletter
    """
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    def perm(model_ct, action, model_cls):
        """Get or create a permission like 'view_article', 'add_newsletter', etc."""
        codename = f"{action}_{model_ct.model}"
        try:
            return Permission.objects.get(content_type=model_ct, codename=codename)
        except Permission.DoesNotExist:
            return Permission.objects.create(
                content_type=model_ct,
                codename=codename,
                name=f"Can {action} {model_cls._meta.verbose_name}",
            )

    # Reader
    reader, _ = Group.objects.get_or_create(name="Reader")
    reader_perms = [
        perm(article_ct, "view", Article),
        perm(newsletter_ct, "view", Newsletter),
    ]
    reader.permissions.set(reader_perms)

    # Editor
    editor, _ = Group.objects.get_or_create(name="Editor")
    editor_perms = [
        perm(article_ct, "view", Article),
        perm(article_ct, "change", Article),
        perm(article_ct, "delete", Article),
        perm(newsletter_ct, "view", Newsletter),
        perm(newsletter_ct, "change", Newsletter),
        perm(newsletter_ct, "delete", Newsletter),
    ]
    editor.permissions.set(editor_perms)

    # Journalist
    journalist, _ = Group.objects.get_or_create(name="Journalist")
    journalist_perms = [
        perm(article_ct, "add", Article),
        perm(article_ct, "view", Article),
        perm(article_ct, "change", Article),
        perm(article_ct, "delete", Article),
        perm(newsletter_ct, "add", Newsletter),
        perm(newsletter_ct, "view", Newsletter),
        perm(newsletter_ct, "change", Newsletter),
        perm(newsletter_ct, "delete", Newsletter),
    ]
    journalist.permissions.set(journalist_perms)


@receiver(post_migrate)
def create_groups_on_migrate(sender, **kwargs):
    """Ensure groups/permissions exist after migrations."""
    _ensure_groups_and_permissions()


@receiver(post_save, sender=Article)
def sync_independent_article(sender, instance: Article, created, **kwargs):
    """
    Keep User.articles_independent in sync:
    - If article.publisher is None, ensure author.articles_independent contains it.
    - Else, ensure it is removed.
    """
    author = instance.author
    if instance.publisher is None:
        author.articles_independent.add(instance)
    else:
        author.articles_independent.remove(instance)

@receiver(post_save, sender=Newsletter)
def sync_independent_newsletter(sender, instance: Newsletter, created, **kwargs):
    author = instance.author
    if instance.publisher is None:
        author.newsletters_independent.add(instance)
    else:
        author.newsletters_independent.remove(instance)

@receiver(pre_save, sender=Article)
def on_article_approval(sender, instance: Article, **kwargs):
    """
    Detect when an article transitions from approved=False -> True, then:
    - Email readers subscribed to the article's publisher OR journalist
    - Optionally post to X using HTTP API via `requests`
    """
    if not instance.pk:
        return  # new article, nothing to compare

    try:
        old = Article.objects.get(pk=instance.pk)
    except Article.DoesNotExist:
        return

    if old.approved is False and instance.approved is True:
        # Gather recipients: subscribers to publisher or journalist
        recipients = set()
        if instance.publisher:
            for reader in instance.publisher.subscribed_readers.all():
                if reader.email:
                    recipients.add(reader.email)
        # Subscribed to the journalist directly
        for reader in instance.author.reader_subscribers.all():
            if reader.email:
                recipients.add(reader.email)

        subject = f"New article approved: {instance.title}"
        body = f"{instance.title}\n\n{instance.content[:500]}..."
        if recipients:
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(recipients),
                    fail_silently=True,
                )
            except Exception as exc:
                logger.warning("Email send failed: %s", exc)

        # Post to X (Twitter) if configured.
        token = getattr(settings, 'X_API_BEARER_TOKEN', '')
        endpoint = getattr(settings, 'X_API_TWEET_ENDPOINT', 'https://api.x.com/2/tweets')
        if token and endpoint:
            try:
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                }
                payload = {'text': f"New article: {instance.title}"}
                # This will work if valid credentials & endpoint are provided.
                requests.post(endpoint, headers=headers, json=payload, timeout=5)
            except Exception as exc:
                logger.info("X post skipped/failed (non-fatal): %s", exc)
