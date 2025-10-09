from django.db import models

# Create your models here.
class StudentProfile(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    year = models.IntegerField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    image = models.FileField(upload_to="media/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Account(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    studentprofile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)

class Club(models.Model):
    image = models.FileField(upload_to="media/", blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

class Member(models.Model):
    role = models.CharField(max_length=50)
    join_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    clubs = models.ManyToManyField(Club, related_name="members")

class Activity(models.Model):
    activity_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="00:00:00")
    location = models.CharField(max_length=100, default="ไม่ระบุ")
    image = models.FileField(upload_to="media/", blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)