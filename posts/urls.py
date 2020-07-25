from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("group/<str:slug>/", views.group_posts),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
            "<str:username>/<int:post_id>/edit/",
            views.post_edit,
            name="post_edit"
    ),
    # path("404/", views.page_not_found, name="page_not_found"),
    # path("500/", views.server_error, name="server_error"),
]
