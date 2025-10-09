from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V

from .models import *
# Create your views here.
def index(request):
    return render(request, "index.html")

def forgot(request):
    return render(request, "forgot.html")

def main(request):
    student = StudentProfile.objects.first()
    club = Club.objects.annotate(member_count=Count('members'))
    activity = Activity.objects.all()

    search = request.GET.get("search", "")
    if search:
        club = club.filter(name__icontains=search)

    return render(request, "main.html", context={
        "student": student,
        "club": club,
        "activity": activity,
        "search": search
    })

def profile(request):
    return render(request, "profile.html")

def admin(request):
    return render(request, "admin.html")

def captain(request):
    return render(request, "captain.html")

def club(request):
    return render(request, "club.html")

def member(request):
    return render(request, "member.html")

def admin(request):
    return render(request, "admin.html")