from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.index, name="index"),
    path("forgot/", views.forgot, name="forgot"),
    path("main/", views.main, name="main"),
    path("profile/", views.profile, name="profile"),
    path("admin/", views.admin, name="admin"),
    path("captain/", views.captain, name="captain"),
    path("club/", views.club, name="club"),
    path("member/", views.member, name="member"),
]