import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.core.paginator import Paginator
from .forms import *
from .models import *


def admin_home(request):
    ###
    allActus = Actus.objects.all()
    paginator = Paginator(allActus, 3)  # 3 actus par page

    page_number = request.GET.get('page')  # Récupérer le numéro de la page
    page_obj = paginator.get_page(page_number)  # Obtenir les objets pour la page actuelle
    ###
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    matiere = Matiere.objects.all()
    total_subject = matiere.count()
    total_course = Filiere.objects.all().count()
    absence_list = Absence.objects.filter(matiere__in=matiere)
    total_attendance = absence_list.count()
    absence_list = []
    subject_list = []
    for subject in matiere:
        attendance_count = Absence.objects.filter(matiere=subject).count()
        subject_list.append(subject.name[:7])
        absence_list.append(attendance_count)
    context = {
        'page_title': "ErayLearning dashboard",
        'page_obj': page_obj,  # Passer les objets paginés au contexte
        'allActus': allActus,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_attendance': total_attendance,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': absence_list

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Ajout Enseignant'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            genre = form.cleaned_data.get('genre')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.genre = genre
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Ajouté avec succée")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Ne peut pas ajouté " + str(e))
        else:
            messages.error(request, "Complèter tous les champs requis")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Ajout Etudiants'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            genre = student_form.cleaned_data.get('genre')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.genre = genre
                user.address = address
                user.student.session = session
                user.student.course = course
                user.save()
                messages.success(request, "Ajouté avec succée")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Ne peut pas ajouté: " + str(e))
        else:
            messages.error(request, "Ne peut pas ajouté: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = FiliereForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Ajout Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Filiere()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)

###################################################################

def add_actus(request):
    #important
    form = ActusForm(request.POST, request.FILES or None)
    context = {
        "form": form,
        "page_title": "Ajout Actus"
    }
    if request.method == 'POST':
        if form.is_valid():
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description")
            image = form.cleaned_data.get("image")
            try:
                actus = Actus(
                    title=title,
                    description=description,
                    image=image  # On assigne l'image directement ici
                )
                actus.save()
                messages.success(request, "Ajout Actus avec succes.")
                return redirect(reverse('add_actus'))
            except Exception as e:
                messages.error(request, f"Ajout Actus Echoué: {str(e)}")
        else:
            messages.error(request, "DATA Ajout Actus Echoué")
    return render(request, 'hod_template/add_actus_template.html', context)

def manage_actus(request):
    allActus = Actus.objects.all()
    context = {
        'allActus': allActus,
        'page_title': 'Gérer les Actus'
    }
    return render(request, "hod_template/manage_actus.html", context)

def edit_actus(request, actus_id):
    instance = get_object_or_404(Actus, id=actus_id)
    form = ActusForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': actus_id,
        'page_title': 'Editer les Actus'
    }
    if request.method == 'POST':
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            image = form.cleaned_data.get('image')
            try:
                actus = Actus.objects.get(id=actus_id)
                actus.title = title
                actus.description = description
                actus.image = image
                actus.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_actus_template.html', context)


def delete_actus(request, actus_id):
    actus = get_object_or_404(Actus, id=actus_id)
    try:
        actus.delete()
        messages.success(request, "Actus deleted successfully!")
    except Exception:
        messages.error(
            request, "Unable to delete the actus")
    return redirect(reverse('manage_actus'))

#Actus
#actus
######################################################################

def add_edt(request):
    #important
    form = EdtForm(request.POST, request.FILES or None)
    context = {
        "form": form,
        "page_title": "Ajout EDT"
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get("matiere")
            filiere = form.cleaned_data.get("filiere")
            image = form.cleaned_data.get("image")
            description = form.cleaned_data.get("description")

            try:
                edt = Edt(
                    matiere=matiere,
                    filiere=filiere,
                    image=image,
                    description=description  # On assigne l'image directement ici
                )
                edt.save()
                messages.success(request, "Ajout EDT avec succes.")
                return redirect(reverse('add_edt'))
            except Exception as e:
                messages.error(request, f"Ajout EDT Echoué: {str(e)}")
        else:
            messages.error(request, "DATA Ajout EDT Echoué")
    return render(request, 'hod_template/add_edt_template.html', context)

def manage_edt(request):
    allEdt = Edt.objects.all()
    context = {
        'allEdt': allEdt,
        'page_title': 'Gérer les EDT'
    }
    return render(request, "hod_template/manage_edt.html", context)

def edit_edt(request, edt_id):
    instance = get_object_or_404(Edt, id=edt_id)
    form = EdtForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': edt_id,
        'page_title': 'Editer les Edt'
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get('matiere')
            filiere = form.cleaned_data.get('filiere')
            image = form.cleaned_data.get('image')
            description = form.cleaned_data.get("description")
            try:
                edt = Edt.objects.get(id=edt_id)
                edt.matiere = matiere
                edt.filiere = filiere
                edt.image = image
                edt.description=description
                edt.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_edt_template.html', context)


def delete_edt(request, edt_id):
    edt = get_object_or_404(Edt, id=edt_id)
    try:
        edt.delete()
        messages.success(request, "Edt deleted successfully!")
    except Exception:
        messages.error(
            request, "Unable to delete the edt")
    return redirect(reverse('manage_edt'))

#Edt
#edt

######################################################################
def add_absence(request):
    #important
    form = AbsenceForm(request.POST, request.FILES or None)
    context = {
        "form": form,
        "page_title": "Ajout Absence"
    }
    if request.method == 'POST':
        if form.is_valid():
            matiere = form.cleaned_data.get("matiere")
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description")
            image = form.cleaned_data.get("image")
            try:
                absence = Absence(
                    matiere=matiere,
                    title=title,
                    description=description,
                    image=image  # On assigne l'image directement ici
                )
                absence.save()
                messages.success(request, "Ajout Absence avec succes.")
                return redirect(reverse('add_absence'))
            except Exception as e:
                messages.error(request, f"Ajout Absence Echoué: {str(e)}")
        else:
            messages.error(request, "DATA Ajout Absence Echoué")
    return render(request, 'hod_template/add_absence_template.html', context)

def manage_absence(request):
    allAbsence = Absence.objects.all()
    context = {
        'allAbsence': allAbsence,
        'page_title': 'Gérer les Absence'
    }
    return render(request, "hod_template/manage_absence.html", context)

def edit_absence(request, absence_id):
    instance = get_object_or_404(Absence, id=absence_id)
    form = AbsenceForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': absence_id,
        'page_title': 'Editer les Absence'
    }
    if request.method == 'POST':
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            image = form.cleaned_data.get('image')
            try:
                absence = Absence.objects.get(id=absence_id)
                absence.title = title
                absence.description = description
                absence.image = image
                absence.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_absence_template.html', context)


def delete_absence(request, absence_id):
    absence = get_object_or_404(Absence, id=absence_id)
    try:
        absence.delete()
        messages.success(request, "Absence deleted successfully!")
    except Exception:
        messages.error(
            request, "Unable to delete the absence")
    return redirect(reverse('manage_absence'))

######################################################################
def add_subject(request):
    form = MatiereForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Ajout Matière'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            filiere = form.cleaned_data.get('filiere')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Matiere()
                subject.name = name
                subject.staff = staff
                subject.filiere = filiere
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Gérer les Enseignants'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Gérer les Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Filiere.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Gérer les Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Matiere.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Gérer les Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Editer les Enseignants'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            genre = form.cleaned_data.get('genre')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.genre = genre
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Editer les Etudiants'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            genre = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.genre = genre
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Filiere, id=course_id)
    form = FiliereForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Editer les Courses'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Filiere.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Matiere, id=subject_id)
    form = MatiereForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Editer les Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Matiere.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Ajout Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Gérer les Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Editer les Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        student_feedback_counts = FeedbackStudent.objects.all().count()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages',
            'student_feedback_counts': student_feedback_counts,
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        staff_feedback_counts = FeedbackStaff.objects.all().count()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages',
            'staff_feedback_counts': staff_feedback_counts,
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Demande de pérmission des ensignants'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Demande de pérmission des etudiants'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Matiere.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Voir les Presences'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('matiere')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Matiere, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'Voir/Editer le Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Envoi Notifications Enseignants",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Envoi Notifications Etudiants",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        # url = "https://fcm.googleapis.com/fcm/send"
        # body = {
        #     'notification': {
        #         'title': "Student Management System",
        #         'body': message,
        #         'click_action': reverse('student_view_notification'),
        #         'icon': static('dist/img/AdminLTELogo.png')
        #     },
        #     'to': student.admin.fcm_token
        # }
        # headers = {'Authorization':
        #            'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
        #            'Content-Type': 'application/json'}
        # data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        # url = "https://fcm.googleapis.com/fcm/send"
        # body = {
        #     'notification': {
        #         'title': "Student Management System",
        #         'body': message,
        #         'click_action': reverse('staff_view_notification'),
        #         'icon': static('dist/img/AdminLTELogo.png')
        #     },
        #     'to': staff.admin.fcm_token
        # }
        # headers = {'Authorization':
        #            'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
        #            'Content-Type': 'application/json'}
        # data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Filiere, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Matiere, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))
