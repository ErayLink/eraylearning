from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    genre = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'genre',  'password','profile_pic', 'address' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['filiere', 'session']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['filiere' ]


class FiliereForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(FiliereForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Filiere


class MatiereForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(MatiereForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Matiere
        fields = ['name', 'staff', 'filiere']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class ActusForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(ActusForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Actus
        fields = ["title", "description", "image"]
        

class AbsenceForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(AbsenceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Absence
        fields = ["matiere","title", "description", "image"]


class EdtForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(EdtForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Edt
        fields = ["matiere","filiere", "image", "description"]

class CoursForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(CoursForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Cours
        fields = ["matiere","title", "description", "link", "video", "poster", "created_by"]


class AddAbsenceForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(AddAbsenceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AddAbsence
        fields = ["matiere", "file", "student"]
    


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    # session_list = Session.objects.all()
    # session_year = forms.ModelChoiceField(
    #     label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['matiere', 'student', 'test', 'exam']
        # widgets = {
        #     "student": forms.SelectMultiple()
        # }


# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#         fields = ['title', 'description', 'students']

# class CoursForm(FormSettings):
#     class Meta:
#         model = Cours
#         fields = ['matiere', 'title', 'description', 'link', 'video']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description du cours'}),
#             'link': forms.URLInput(attrs={'placeholder': 'Lien vers le cours'}),
#             #'students': forms.SelectMultiple(),  # Menu déroulant multiple
#         }

