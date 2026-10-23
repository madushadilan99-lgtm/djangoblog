from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db import models

from .models import Post, Category, Comment
from .forms import PostForm, RegisterForm, CommentForm


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(
            status="published"
        ).order_by("-created_at")

        category_name = self.request.GET.get(
            "category", ""
        ).strip()

        search_query = self.request.GET.get(
            "q", ""
        ).strip()

        if category_name:
            queryset = queryset.filter(
                category__name__iexact=category_name
            )

        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query)
                | models.Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get(
            "category", ""
        ).strip()
        context["search_query"] = self.request.GET.get(
            "q", ""
        ).strip()

        return context


class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    paginate_by = 6
    login_url = "login"

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).order_by("-created_at")


class CategoryPostsView(ListView):
    model = Post
    template_name = "blog/category_posts.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            pk=self.kwargs["pk"],
        )

        return Post.objects.filter(
            status="published",
            category=self.category,
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["categories"] = Category.objects.all()

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                models.Q(status="published")
                | models.Q(author=self.request.user)
            )

        return Post.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["comments"] = self.object.comments.select_related(
            "author"
        ).order_by("-created_at")

        context["comment_form"] = CommentForm()

        return context


def add_comment(request, slug):
    if not request.user.is_authenticated:
        messages.info(
            request,
            "Please log in to leave a comment.",
        )
        return redirect("login")

    post = get_object_or_404(
        Post.objects.filter(status="published"),
        slug=slug,
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            messages.success(
                request,
                "Comment added successfully!",
            )
        else:
            messages.error(
                request,
                "Please enter a valid comment.",
            )

    return redirect("post_detail", slug=post.slug)


def delete_comment(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    comment = get_object_or_404(
        Comment.objects.select_related(
            "post",
            "post__author",
        ),
        pk=pk,
    )

    if request.method == "POST":
        if (
            comment.author == request.user
            or comment.post.author == request.user
        ):
            post_slug = comment.post.slug
            comment.delete()

            messages.success(
                request,
                "Comment deleted successfully!",
            )

            return redirect(
                "post_detail",
                slug=post_slug,
            )

        messages.error(
            request,
            "You do not have permission to delete this comment.",
        )

        return redirect(
            "post_detail",
            slug=comment.post.slug,
        )

    return redirect(
        "post_detail",
        slug=comment.post.slug,
    )


def about(request):
    return render(
        request,
        "blog/about.html",
        {"content": "This is the Djangoblog team."},
    )


def contact(request):
    return render(
        request,
        "blog/contact.html",
        {"contact": "This is the Contact Page."},
    )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user

        messages.success(
            self.request,
            "Post created successfully!",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug},
        )


class PostUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Post updated successfully!",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug},
        )


class PostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Post deleted successfully!",
        )

        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "blog/register.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response


def custom_403(request, exception):
    return render(
        request,
        "blog/403.html",
        status=403,
    )