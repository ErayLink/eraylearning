import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from .forms import *
from .models import *


def staff_home(request):
        ###
    allActus = Actus.objects.all()
    paginator = Paginator(allActus, 3)  # 3 actus par page

    page_number = request.GET.get('page')  # Récupérer le numéro de la page
    page_obj = paginator.get_page(page_number)  # Obtenir les objets pour la page actuelle
    ###
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(filiere=staff.filiere).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Matiere.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(matiere__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(matiere=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_obj': page_obj,  # Passer les objets paginés au contexte
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.filiere) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Matiere.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'List Presence'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('matiere')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Matiere, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            filiere_id=subject.filiere.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e



@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Matiere, id=subject_id)

        # Check if an attendance object already exists for the given date and session
        attendance, created = Attendance.objects.get_or_create(session=session, matiere=subject, date=date)

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))

            # Check if an attendance report already exists for the student and the attendance object
            attendance_report, report_created = AttendanceReport.objects.get_or_create(student=student, attendance=attendance)

            # Update the status only if the attendance report was newly created
            if report_created:
                attendance_report.status = student_dict.get('status')
                attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Matiere.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Mis a jours du Présence'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Ajout Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'Voir/Mettre a jours le Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "Voir les Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    form = EditResultForm(request.POST or None)
    staff = get_object_or_404(Staff, admin=request.user)
    matieres = Matiere.objects.filter(staff=staff)
    #sessions = Session.objects.all()
    context = {
        'form': form,
        'page_title': 'Resultat / Notes',
        'matieres': matieres,
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            print(student_id)
            matiere_id = request.POST.get('matiere')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            matieres = get_object_or_404(Matiere, id=matiere_id)
            try:
                data = StudentResult(student=student, matiere=matieres)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Notes Ajouter")
            except:
                result = StudentResult(student=student, matiere=matieres, test=test, exam=exam)
                result.save()
                messages.success(request, "Notes Saved")
        except Exception as e:
            messages.warning(request, f"Error Occured While Processing Form: {str(e)}")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('matiere')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Matiere, id=subject_id)
        result = StudentResult.objects.get(student=student, matiere=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')
    

# @csrf_exempt
# def add_course(request):
#     if request.method == 'POST':
#         form = CourseForm(request.POST)
#         if form.is_valid():
#             course = form.save(commit=False)
#             course.created_by = request.user  # Enregistrer l'utilisateur qui a créé le cours
#             course.save()
#             return redirect('course_list')  # Rediriger vers une page de liste de cours
#     else:
#         form = CourseForm()
    
#     return render(request, 'add_course.html', {'form': form})


######################################################################

def add_cours(request):

    #important
    form = CoursForm(request.POST, request.FILES or None)
    context = {
        "form": form,
        "page_title": "Ajout Cours"
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get("matiere")
            link = form.cleaned_data.get("link")
            video = form.cleaned_data.get("video")
            # students = form.cleaned_data.get("students")
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description")
            video = form.cleaned_data.get("video")
            image = form.cleaned_data.get("poster")
            creator = request.user.username

            try:
                cours = Cours(
                    matiere=matiere,
                    link=link,
                    # students=students,
                    video=video,
                    poster=image,
                    title=title,
                    description=description,
                    created_by=creator
                    # image=image  # On assigne l'image directement ici
                )
                cours.save()
                messages.success(request, "Ajout Cours avec succes.")
                return redirect(reverse('staff_add_cours'))
            except Exception as e:
                messages.error(request, f"Ajout Cours Echoué: {str(e)}")
        else:
            messages.error(request, "DATA Ajout Cours Echoué")
    return render(request, 'staff_template/staff_add_cours.html', context)

def manage_cours(request):
        ###
    allCours = Cours.objects.all()
    paginator = Paginator(allCours, 3)  # 3 actus par page

    page_number = request.GET.get('page')  # Récupérer le numéro de la page
    page_obj = paginator.get_page(page_number)  # Obtenir les objets pour la page actuelle
    ###
    context = {
        'page_obj': page_obj,
        'allCours': allCours,
        'page_title': 'Gérer les Cours'
    }
    return render(request, "staff_template/staff_list_cours.html", context)

def edit_cours(request, cours_id):
    allActus = Cours.objects.all()
    paginator = Paginator(allActus, 3)  # 3 actus par page

    page_number = request.GET.get('page')  # Récupérer le numéro de la page
    page_obj = paginator.get_page(page_number)  # Obtenir les objets pour la page actuelle
    ###
    instance = get_object_or_404(Cours, id=cours_id)
    form = CoursForm(request.POST or None, instance=instance)
    context = {
        'page_obj': page_obj,
        'form': form,
        'course_id': cours_id,
        'page_title': 'Editer les Cours'
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get("matiere")
            link = form.cleaned_data.get("link")
            video = form.cleaned_data.get("video")
            #students = form.cleaned_data.get("students")
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description")
            image = form.cleaned_data.get("image")

            try:
                cours = Cours.objects.get(id=cours_id)
                cours.title = title
                cours.description = description
                # cours.image = image
                cours.link = link
                # cours.students = students
                cours.video = video
                cours.matiere = matiere
                cours.image = image
                cours.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_cours_template.html', context)


def delete_cours(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id)
    try:
        cours.delete()
        messages.success(request, "Cours deleted successfully!")
    except Exception:
        messages.error(
            request, "Unable to delete the cours")
    return redirect(reverse('manage_cours'))


def add_absence(request):

    #important
    form = AddAbsenceForm(request.POST, request.FILES or None)
    context = {
        "form": form,
        "page_title": "Ajout Absence"
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get("matiere")
            file = form.cleaned_data.get("file")
            student = form.cleaned_data.get("student")
            try:
                absence = AddAbsence(
                    matiere=matiere,
                    student=student,
                    file=file
                )
                absence.save()
                messages.success(request, "Ajout Absence avec succes.")
                return redirect(reverse('staff_add_absence'))
            except Exception as e:
                messages.error(request, f"Ajout Absence Echoué: {str(e)}")
        else:
            messages.error(request, "DATA Ajout Absence Echoué")
    return render(request, 'staff_template/staff_add_absence.html', context)


def list_absence(request):
    #student = get_object_or_404(Student, admin=request.user)
    allAbsence = AddAbsence.objects.all()
    paginator = Paginator(allAbsence, 3)  # 3 actus par page

    page_number = request.GET.get('page')  # Récupérer le numéro de la page
    page_obj = paginator.get_page(page_number)  # Obtenir les objets pour la page actuelle
    context = {
        'page_obj': page_obj,
        'page_title': 'Liste des Absences'
    }

    return render(request, "staff_template/staff_list_absence.html", context)


def staff_view_result(request):
    #student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.all()
    context = {
        'results': results,
        'page_title': "Notes"
    }
    return render(request, "staff_template/staff_view_result.html", context)

######################################################################
