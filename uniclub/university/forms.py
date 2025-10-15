from django import forms
from .models import *
from django.contrib.auth.models import User
from .models import StudentProfile, Account
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm

class SignUpForm(forms.Form):
    FACULTY_CHOICES = [
        ('คณะวิศวกรรมศาสตร์', 'คณะวิศวกรรมศาสตร์'),
        ('คณะสถาปัตยกรรม ศิลปะและการออกแบบ', 'คณะสถาปัตยกรรม ศิลปะและการออกแบบ'),
        ('คณะครุศาสตร์อุตสาหกรรมและเทคโนโลยี', 'คณะครุศาสตร์อุตสาหกรรมและเทคโนโลยี'),
        ('คณะเทคโนโลยีการเกษตร', 'คณะเทคโนโลยีการเกษตร'),
        ('คณะวิทยาศาสตร์', 'คณะวิทยาศาสตร์'),
        ('คณะอุตสาหกรรมอาหาร', 'คณะอุตสาหกรรมอาหาร'),
        ('คณะเทคโนโลยีสารสนเทศ', 'คณะเทคโนโลยีสารสนเทศ'),
        ('คณะบริหารธุรกิจ', 'คณะบริหารธุรกิจ'),
        ('คณะศิลปศาสตร์', 'คณะศิลปศาสตร์'),
        ('คณะแพทยศาสตร์', 'คณะแพทยศาสตร์'),
        ('คณะทันตแพทยศาสตร์', 'คณะทันตแพทยศาสตร์'),
        ('คณะพยาบาลศาสตร์', 'คณะพยาบาลศาสตร์'),
    ]

    YEAR_CHOICES = [(i, str(i)) for i in range(1, 9)]

    first_name = forms.CharField(max_length=100, label="ชื่อ")
    last_name = forms.CharField(max_length=100, label="นามสกุล")
    student_id = forms.CharField(max_length=10, label="รหัสนักศึกษา")
    faculty = forms.ChoiceField(choices=FACULTY_CHOICES, label="คณะ")
    year = forms.ChoiceField(choices=YEAR_CHOICES, label="ชั้นปี")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=10, required=False, label="เบอร์โทรศัพท์")
    password = forms.CharField(widget=forms.PasswordInput, label="รหัสผ่าน")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="ยืนยันรหัสผ่าน")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("รหัสผ่านไม่ตรงกัน")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@kmitl.ac.th"):
            raise forms.ValidationError("Email ต้องลงท้ายด้วย @kmitl.ac.th")
        elif Account.objects.filter(email=email).exists():
            raise forms.ValidationError("Email นี้ถูกใช้งานแล้ว")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("รหัสนักศึกษานี้มีอยู่แล้ว")
        return student_id

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("เบอร์โทรศัพท์ต้องมี 10 หลักและเป็นตัวเลขเท่านั้น")
        return phone
    
    def save(self):
        data = self.cleaned_data
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
        return account
    
class CreateClubForm(ModelForm):
    class Meta:
        model = ClubRequest
        fields = [
            'name',
            'description',
            'location',
            'image',
        ]

class StudentProfileForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'student_id',
            'first_name',
            'last_name',
            'faculty',
            'year',
            'email',
            'phone',
            'image',
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@kmitl.ac.th"):
            raise forms.ValidationError("Email ต้องลงท้ายด้วย @kmitl.ac.th")
        if StudentProfile.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email นี้ถูกใช้งานแล้ว")
        return email
    
    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year < 1 or year > 8:
            raise forms.ValidationError("ชั้นปีต้องอยู่ระหว่าง 1-8")
        return year
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("รหัสนักศึกษานี้มีอยู่แล้ว")
        return student_id

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("เบอร์โทรศัพท์ต้องมี 10 หลักและเป็นตัวเลขเท่านั้น")
        return phone