from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("forgot/", views.forgot, name="forgot"),

    path("main/", views.main, name="main"),
    path("create-club/", views.create_club, name="create_club"),
    path("profile/", views.profile, name="profile"),
    path("join-club/", views.join_club, name="join_club"),

    path("approve_request/<int:request_id>/", views.approve_request, name="approve_request"),
    path("reject_request/<int:request_id>/", views.reject_request, name="reject_request"),
    path("club/", views.club, name="club"),
    path("member/", views.member, name="member"),

    path("create-activity/", views.create_activity, name="create_activity"),
    path('activity/delete/<int:id>/', views.delete_activity, name='delete-activity'),

    path("admins/", views.admin, name="admin"),
    path("approve-club/<int:request_id>/", views.approve_club_request, name="approve_club"),
    path("reject-club/<int:request_id>/", views.reject_club_request, name="reject_club"),
    path('delete-club/<int:club_id>/', views.delete_club, name='delete_club'),
]