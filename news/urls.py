from django.urls import path
from . import views

urlpatterns = [

path('read/publishers/', views.publishers_list, name='publishers_list'),
path('read/publishers/<int:pk>/toggle/', views.toggle_publisher_subscription, name='toggle_publisher_subscription'),

path('journalist/', views.journalist_dashboard, name='journalist_dashboard'),
path('journalist/articles/new/', views.article_create, name='article_create'),
path('journalist/articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
path('journalist/articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
path('journalist/newsletters/new/', views.newsletter_create, name='newsletter_create'),
path('journalist/newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter_edit'),
path('journalist/newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter_delete'),

    path('accounts/register/', views.register, name='register'),
    path('', views.home, name='home'),
    # Editor UI
    path('editor/pending/', views.pending_articles, name='pending_articles'),
    path('editor/approve/<int:pk>/', views.approve_article, name='approve_article'),

    # API
    path('api/feed/', views.ReaderFeedView.as_view(), name='api_feed'),
    path('api/publishers/<int:pk>/articles/', views.PublisherArticlesView.as_view(), name='api_publisher_articles'),
    path('api/journalists/<int:pk>/articles/', views.JournalistArticlesView.as_view(), name='api_journalist_articles'),
]
