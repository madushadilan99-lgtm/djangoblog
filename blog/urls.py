from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    PostListView,
    CategoryPostsView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    MyPostsView,
    about,
    contact,
    add_comment,
    delete_comment,
    RegisterView,
)


urlpatterns = [
    # Home
    path(
        "",
        PostListView.as_view(),
        name="home",
    ),

    # Category Posts
    path(
        "category/<int:pk>/",
        CategoryPostsView.as_view(),
        name="category_posts",
    ),

    # Password Reset - Step 1
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="blog/password_reset.html"
        ),
        name="password_reset",
    ),

    # Password Reset - Step 2
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),

    # Password Reset - Step 3
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    # Password Reset - Step 4
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),

    # My Posts
    path(
        "my-posts/",
        MyPostsView.as_view(),
        name="my_posts",
    ),

    # Register
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # Create Post
    path(
        "posts/new/",
        PostCreateView.as_view(),
        name="post_create",
    ),

    # Edit Post
    path(
        "posts/<slug:slug>/edit/",
        PostUpdateView.as_view(),
        name="post_edit",
    ),

    # Delete Post
    path(
        "posts/<slug:slug>/delete/",
        PostDeleteView.as_view(),
        name="post_delete",
    ),

    # Add Comment
    path(
        "posts/<slug:slug>/comment/",
        add_comment,
        name="add_comment",
    ),

    # Delete Comment
    path(
        "comments/<int:pk>/delete/",
        delete_comment,
        name="delete_comment",
    ),

    # Post Detail
    path(
        "posts/<slug:slug>/",
        PostDetailView.as_view(),
        name="post_detail",
    ),

    # About
    path(
        "about/",
        about,
        name="about",
    ),

    # Contact
    path(
        "contact/",
        contact,
        name="contact",
    ),
]