from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User, Publisher, Article

class APISubscriptionTests(TestCase):
    def setUp(self):
        # Users
        self.reader = User.objects.create_user(username='reader', password='test123', role=User.Roles.READER, email='reader@example.com')
        self.editor = User.objects.create_user(username='editor', password='test123', role=User.Roles.EDITOR, email='editor@example.com')
        self.journalist1 = User.objects.create_user(username='jour1', password='test123', role=User.Roles.JOURNALIST, email='j1@example.com')
        self.journalist2 = User.objects.create_user(username='jour2', password='test123', role=User.Roles.JOURNALIST, email='j2@example.com')

        # Publishers
        self.pub1 = Publisher.objects.create(name='Publisher One')
        self.pub2 = Publisher.objects.create(name='Publisher Two')

        # Link staff to publishers (not required for tests but realistic)
        self.pub1.editors.add(self.editor)
        self.pub1.journalists.add(self.journalist1)
        self.pub2.journalists.add(self.journalist2)

        # Reader subscriptions
        self.reader.subscriptions_publishers.add(self.pub1)
        self.reader.subscriptions_journalists.add(self.journalist1)

        # Articles
        self.a1 = Article.objects.create(title='A1', content='...', author=self.journalist1, publisher=self.pub1, approved=True)
        self.a2 = Article.objects.create(title='A2', content='...', author=self.journalist2, publisher=self.pub2, approved=True)
        self.a3 = Article.objects.create(title='A3', content='...', author=self.journalist1, publisher=self.pub1, approved=False)
        self.a4 = Article.objects.create(title='A4', content='independent', author=self.journalist1, publisher=None, approved=True)

        self.client = APIClient()

    def test_feed_returns_only_subscribed_sources(self):
        self.client.login(username='reader', password='test123')
        url = reverse('api_feed')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        ids = [a['id'] for a in resp.json()]
        # A1 qualifies: approved, publisher in subs, author in subs
        # A4 qualifies: approved independent by jour1 (author in subs)
        # A2 should NOT appear (publisher/author not in subs)
        # A3 not approved
        self.assertIn(self.a1.id, ids)
        self.assertIn(self.a4.id, ids)
        self.assertNotIn(self.a2.id, ids)
        self.assertNotIn(self.a3.id, ids)

    def test_publisher_endpoint_only_returns_that_publishers_articles(self):
        self.client.login(username='reader', password='test123')
        url = reverse('api_publisher_articles', kwargs={'pk': self.pub1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        titles = [a['title'] for a in resp.json()]
        self.assertIn('A1', titles)
        self.assertNotIn('A2', titles)
        self.assertNotIn('A3', titles)  # not approved

    def test_journalist_endpoint_only_returns_that_journalists_articles(self):
        self.client.login(username='reader', password='test123')
        url = reverse('api_journalist_articles', kwargs={'pk': self.journalist1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        titles = [a['title'] for a in resp.json()]
        self.assertIn('A1', titles)
        self.assertIn('A4', titles)  # independent, approved
        self.assertNotIn('A2', titles)  # different journalist
