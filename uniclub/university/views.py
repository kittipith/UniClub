from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from .models import *
from .forms import SignUpForm, CreateClubForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

def index(request):
    return render(request, "index.html")


from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            user.set_password(data['password'])
            user.save()

            student = StudentProfile.objects.create(
                student_id=data['student_id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                faculty=data['faculty'],
                year=data['year'],
                email=data['email'],
                phone=data.get('phone', '')
            )

            account = Account.objects.create(
                email=data['email'],
                password=make_password(data['password']),
                studentprofile=student
            )
            Member.objects.create(
                account=account,
                role=Member.Role.MEMBER
            )
            auth_login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_object = User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(request, "ไม่พบบัญชีนี้")
            return render(request, 'index.html')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)

            try:
                account = Account.objects.get(email=email)
                member = Member.objects.get(account=account)
            except (Account.DoesNotExist, Member.DoesNotExist):
                messages.error(request, "ไม่พบข้อมูล role")
                return render(request, 'index.html')

            if member.role == Member.Role.MEMBER:
                return redirect('main')
            elif member.role == Member.Role.LEADER:
                return redirect('captain')
            elif member.role == Member.Role.ADMIN:
                return redirect('admin')
            else:
                messages.error(request, "Role ไม่ถูกต้อง")
                return render(request, 'index.html')

        else:
            messages.error(request, "รหัสผ่านไม่ถูกต้อง")
            return render(request, 'index.html')

    return render(request, 'index.html')

def forgot(request):
    return render(request, "forgot.html")

def logout(request):
    auth_logout(request)
    return redirect('index')

def main(request):
    if not request.user.is_authenticated:
        return redirect('login')

    student = StudentProfile.objects.first()
    club = Club.objects.annotate(member_count=Count('members'))
    activity = Activity.objects.all()

    search = request.GET.get("search", "")
    if search:
        club = club.filter(name__icontains=search)

    return render(request, "main.html", {
        "student": student,
        "club": club,
        "activity": activity,
        "search": search,
        "user": request.user,
    })

def create_club(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        location = request.POST.get('location')
        image = request.FILES.get('image')

        try:
            account = Account.objects.get(email=request.user.email)
        except Account.DoesNotExist:
            messages.error(request, "ไม่พบข้อมูลผู้ใช้ในระบบ Account")
            return redirect('main')

        ClubRequest.objects.create(
            name=name,
            description=description,
            location=location,
            image=image,
            requested_by=account,
            status='PENDING'
        )

        messages.success(request, "ส่งคำขอสร้างชมรมเรียบร้อย รอการอนุมัติจากผู้ดูแล")
        return redirect('main')

    return redirect('main')



def approve_club_request(request, request_id):
    club_request = ClubRequest.objects.get(id=request_id)

    Club.objects.create(
        name=club_request.name,
        description=club_request.description,
        location=club_request.location,
        image=club_request.image
    )

    club_request.status = 'APPROVED'
    club_request.save()

    account = club_request.requested_by
    try:
        member = Member.objects.get(account=account)
        member.role = Member.Role.LEADER
        member.save()
    except Member.DoesNotExist:
        messages.error(request, "ไม่พบข้อมูลสมาชิกของผู้ขอ")
        return redirect('admin')

    messages.success(request, f"อนุมัติชมรม {club_request.name} เรียบร้อย ผู้ใช้กลายเป็น LEADER แล้ว")
    return redirect('admin')

def reject_club_request(request, request_id):
    if request.method != 'POST':
        return redirect('admin')

    club_request = ClubRequest.objects.get(id=request_id)
    club_request.status = 'REJECTED'
    club_request.save()
    messages.success(request, f"ปฏิเสธชมรม {club_request.name} เรียบร้อย")
    return redirect('admin')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "profile.html")

def captain(request):
    if not request.user.is_authenticated:
        return redirect('login')
    student = StudentProfile.objects.first()
    club = Club.objects.annotate(member_count=Count('members'))
    activity = Activity.objects.all()

    search = request.GET.get("search", "")
    if search:
        club = club.filter(name__icontains=search)

    return render(request, "captain.html", {
        "student": student,
        "club": club,
        "activity": activity,
        "search": search,
        "user": request.user,
    })

def club(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        club_id = request.POST.get('club_id')
        club = get_object_or_404(Club, id=club_id)

        try:
            account = Account.objects.get(email=request.user.email)
            member = Member.objects.get(account=account)
        except (Account.DoesNotExist, Member.DoesNotExist):
            messages.error(request, "ไม่พบข้อมูลผู้ใช้ในระบบ Account หรือ Member")
            return redirect('main')

        if club.members.filter(id=member.id).exists():
            messages.info(request, "คุณเป็นสมาชิกชมรมนี้อยู่แล้ว")
        else:
            club.members.add(member)
            messages.success(request, f"สมัครเข้าชมรม {club.name} เรียบร้อย")

        return redirect('main')

    return render(request, "club.html", {
        "user": request.user,
        "clubs": club,
        "members": member,
    })

def member(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, "member.html")

def admin(request):
    if not request.user.is_authenticated:
        return redirect('login')

    club_requests = ClubRequest.objects.filter(status='PENDING')
    club = Club.objects.all()
    student = StudentProfile.objects.all()
    total_club = club.count()
    total_student = student.count()
    total_requests = club_requests.count()

    return render(request, "admin.html", {
        "club_requests": club_requests,
        "club": club,
        "student": student,
        "total_club": total_club,
        "total_student": total_student,
        "total_requests": total_requests,
    })