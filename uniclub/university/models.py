from django.db import models
from django.utils import timezone

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

class Club(models.Model):
    image = models.FileField(upload_to="media/", blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    leader = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)

class Account(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    studentprofile = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)

class Member(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        LEADER = 'LEADER', 'Leader'
        MEMBER = 'MEMBER', 'Member'

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.MEMBER)
    join_date = models.DateField(auto_now_add=True)
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    clubs = models.ManyToManyField(Club, related_name="members", blank=True)

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

class ClubRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติ'),
        ('REJECTED', 'ปฏิเสธ'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to="media/", blank=True, null=True)

    requested_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)

class MemberRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติ'),
        ('REJECTED', 'ปฏิเสธ'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=Member.Role.choices, default=Member.Role.MEMBER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)