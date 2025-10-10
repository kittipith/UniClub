from django import forms
from .models import *
from django.contrib.auth.models import User
from .models import StudentProfile, Account
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm

class SignUpForm(forms.Form):
    FACULTY_CHOICES = [
        ('engineer', 'คณะวิศวกรรมศาสตร์'),
        ('architec', 'คณะสถาปัตยกรรม ศิลปะและการออกแบบ'),
        ('teacher', 'คณะครุศาสตร์อุตสาหกรรมและเทคโนโลยี'),
        ('farmer', 'คณะเทคโนโลยีการเกษตร'),
        ('science', 'คณะวิทยาศาสตร์'),
        ('food', 'คณะอุตสาหกรรมอาหาร'),
        ('it', 'คณะเทคโนโลยีสารสนเทศ'),
        ('ceo', 'คณะบริหารธุรกิจ'),
        ('art', 'คณะศิลปศาสตร์'),
        ('docter', 'คณะแพทยศาสตร์'),
        ('dentist', 'คณะทันตแพทยศาสตร์'),
        ('nurse', 'คณะพยาบาลศาสตร์'),
        ('adap', 'คณะเทคโนโลยีนวัตกรรมบูรณาการ'),
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
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
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
            raise forms.ValidationError("เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลัก")
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