from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from .models import *
from .forms import SignUpForm, CreateClubForm, StudentProfileForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

def index(request):
    return render(request, "index.html")
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
                return redirect('club')
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
    
    account = get_object_or_404(Account, email=request.user.email)
    student = account.studentprofile
    member = get_object_or_404(Member, account=account)
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
        "member": member,
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
def profile(request):
    account = get_object_or_404(Account, email=request.user.email)
    student = account.studentprofile

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, "profile.html", {
        "form": form, 
        "student": student
    })

def join_club(request):
    if request.method == 'POST':
        club_id = request.POST.get('club_id')
        if not club_id:
            messages.error(request, "ไม่พบรหัสชมรม")
            return redirect('main')

        club = get_object_or_404(Club, id=club_id)
        account = get_object_or_404(Account, email=request.user.email)

        is_already_member = Member.objects.filter(account=account, clubs=club).exists()
        has_pending_request = MemberRequest.objects.filter(account=account, club=club, status='PENDING').exists()

        if is_already_member:
            messages.warning(request, f"คุณเป็นสมาชิกของชมรม {club.name} อยู่แล้ว")
        elif has_pending_request:
            messages.warning(request, f"คุณได้ส่งคำขอเข้าร่วมชมรม {club.name} ไปแล้ว")
        else:
            MemberRequest.objects.create(
                account=account,
                club=club,
                status='PENDING'
            )
            messages.success(request, f"ส่งคำขอเข้าร่วมชมรม {club.name} เรียบร้อยแล้ว")
    
    return redirect('main')

def club(request):
    if not request.user.is_authenticated:
        return redirect('login')

    account = get_object_or_404(Account, email=request.user.email)
    club = Club.objects.filter(leader=account).first()

    member_requests = []
    total_requests = 0
    activities = []
    if club:
        member_requests = MemberRequest.objects.filter(club=club, status='PENDING')
        total_requests = member_requests.count()
        activities = Activity.objects.filter(club=club).order_by('-start_date')  # ดึงกิจกรรมของชมรม

    context = {
        'club': club,
        'account': account,
        'member_requests': member_requests,
        'total_requests': total_requests,
        'activities': activities,
        'total_activity': activities.count()
    }
    return render(request, 'club.html', context)


def approve_request(request, request_id):
    if request.method != 'POST':
        messages.error(request, "Method not allowed.")
        return redirect('club')

    member_request = get_object_or_404(MemberRequest, id=request_id)

    try:
        leader_account = get_object_or_404(Account, email=request.user.email)
    except:
        messages.error(request, "ไม่พบบัญชีผู้ใช้ในระบบ")
        return redirect('club')

    if member_request.club.leader != leader_account:
        messages.error(request, "คุณไม่มีสิทธิ์อนุมัติคำขอนี้")
        return redirect('club')
    
    if member_request.status != 'PENDING':
        messages.info(request, "คำขอนี้ถูกดำเนินการไปแล้ว")
        return redirect('club')

    member_obj, created = Member.objects.get_or_create(account=member_request.account)
    member_obj.clubs.add(member_request.club)
    member_obj.save()

    member_request.status = 'APPROVED'
    member_request.save()

    messages.success(request, f"อนุมัติ {member_request.account.studentprofile.first_name} เรียบร้อย")
    return redirect('club')


def reject_request(request, request_id):
    if request.method != 'POST':
        messages.error(request, "Method not allowed.")
        return redirect('club')

    member_request = get_object_or_404(MemberRequest, id=request_id)

    member_request.status = 'REJECTED'
    member_request.save()

    messages.success(request, f"ปฏิเสธคำขอของ {member_request.account.studentprofile.first_name} เรียบร้อย")
    return redirect('club')

@csrf_protect
def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    activities = Activity.objects.filter(club=club).order_by('-start_date')
    return render(request, 'club.html', {
        'club': club,
        'activities': activities,
    })

def create_activity(request):
    if request.method == 'POST':
        account = get_object_or_404(Account, email=request.user.email)
        club = get_object_or_404(Club, leader=account)

        Activity.objects.create(
            club=club,
            activity_name=request.POST['name'],
            description=request.POST.get('description', ''),
            location=request.POST.get('location', ''),
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time']
        )
        # redirect กลับหน้า club
        return redirect('club')

def delete_activity(request, id):
    activity = get_object_or_404(Activity, id=id)
    activity.delete()
    return redirect('club')

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

def approve_club_request(request, request_id):
    club_request = ClubRequest.objects.get(id=request_id)

    account = club_request.requested_by
    club = Club.objects.create(
        name=club_request.name,
        description=club_request.description,
        location=club_request.location,
        image=club_request.image,
        leader=account
    )

    club_request.status = 'APPROVED'
    club_request.save()

    try:
        member = Member.objects.get(account=account)
        member.role = Member.Role.LEADER
        member.clubs.add(club)
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
def delete_club(request, club_id):
    if request.method == 'POST':
        club = get_object_or_404(Club, id=club_id)
        leader_account = club.leader

        try:
            member = Member.objects.get(account=leader_account)
            member.clubs.remove(club)
            member.role = Member.Role.MEMBER
            member.save()
        except Member.DoesNotExist:
            messages.warning(request, "ไม่พบ Member สำหรับหัวหน้าชมรมนี้")

        club.delete()
        messages.success(request, f"ปิดชมรม {club.name} เรียบร้อย")

    return redirect('admin')