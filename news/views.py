
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from django.urls import reverse
from django.views.decorators.http import require_POST

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Article, Publisher, User, Newsletter
from .forms import SignUpForm, ArticleForm, NewsletterForm
from .serializers import ArticleSerializer

def is_editor(user):
    return user.is_authenticated and user.role == User.Roles.EDITOR

def is_journalist(user):
    return user.is_authenticated and user.role == User.Roles.JOURNALIST

# ---- Basic pages ----
def home(request):
    return render(request, 'news/home.html')

@login_required
@user_passes_test(is_editor)
def pending_articles(request):
    articles = Article.objects.filter(approved=False).order_by("-created_at")
    return render(request, "news/pending_articles.html", {"articles": articles})

@login_required
@user_passes_test(is_editor)
@require_POST
def approve_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save(update_fields=["approved"])
    return HttpResponseRedirect(reverse("pending_articles"))

# ---- Reader UI ----
@login_required
def publishers_list(request):
    pubs = Publisher.objects.all()
    subs = set(request.user.subscriptions_publishers.values_list("id", flat=True))
    return render(request, "news/publishers_list.html", {"publishers": pubs, "subs": subs})

@login_required
@require_POST
def toggle_publisher_subscription(request, pk):
    pub = get_object_or_404(Publisher, pk=pk)
    if request.user.subscriptions_publishers.filter(id=pub.id).exists():
        request.user.subscriptions_publishers.remove(pub)
    else:
        request.user.subscriptions_publishers.add(pub)
    return redirect("publishers_list")

# ---- Journalist UI ----
@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    arts = Article.objects.filter(author=request.user).order_by("-created_at")
    nls = Newsletter.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "news/journalist_dashboard.html", {"articles": arts, "newsletters": nls})

@login_required
@user_passes_test(is_journalist)
def article_create(request):
    form = ArticleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        art = form.save(commit=False)
        art.author = request.user
        art.approved = False
        art.save()
        return redirect("journalist_dashboard")
    return render(request, "news/article_form.html", {"form": form, "mode": "create"})

@login_required
@user_passes_test(is_journalist)
def article_edit(request, pk):
    art = get_object_or_404(Article, pk=pk, author=request.user)
    form = ArticleForm(request.POST or None, instance=art)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("journalist_dashboard")
    return render(request, "news/article_form.html", {"form": form, "mode": "edit"})

@login_required
@user_passes_test(is_journalist)
def article_delete(request, pk):
    art = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == "POST":
        art.delete()
        return redirect("journalist_dashboard")
    return render(request, "news/article_confirm_delete.html", {"article": art})

@login_required
@user_passes_test(is_journalist)
def newsletter_create(request):
    form = NewsletterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        nl = form.save(commit=False)
        nl.author = request.user
        nl.save()
        return redirect("journalist_dashboard")
    return render(request, "news/newsletter_form.html", {"form": form, "mode": "create"})

@login_required
@user_passes_test(is_journalist)
def newsletter_edit(request, pk):
    nl = get_object_or_404(Newsletter, pk=pk, author=request.user)
    form = NewsletterForm(request.POST or None, instance=nl)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("journalist_dashboard")
    return render(request, "news/newsletter_form.html", {"form": form, "mode": "edit"})

@login_required
@user_passes_test(is_journalist)
def newsletter_delete(request, pk):
    nl = get_object_or_404(Newsletter, pk=pk, author=request.user)
    if request.method == "POST":
        nl.delete()
        return redirect("journalist_dashboard")
    return render(request, "news/newsletter_confirm_delete.html", {"newsletter": nl})

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
    else:
        form = SignUpForm()
    return render(request, "news/register.html", {"form": form})

# ---- API ----
class ReaderFeedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        pub_ids = request.user.subscriptions_publishers.values_list("id", flat=True)
        jour_ids = request.user.subscriptions_journalists.values_list("id", flat=True)
        qs = Article.objects.filter(approved=True).filter(
            models.Q(publisher_id__in=pub_ids) | models.Q(author_id__in=jour_ids)
        ).order_by("-created_at")
        return Response(ArticleSerializer(qs, many=True).data)

class PublisherArticlesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        qs = Article.objects.filter(approved=True, publisher_id=pk).order_by("-created_at")
        return Response(ArticleSerializer(qs, many=True).data)

class JournalistArticlesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        qs = Article.objects.filter(approved=True, author_id=pk).order_by("-created_at")
        return Response(ArticleSerializer(qs, many=True).data)
