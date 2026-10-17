from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AcademicGroupForm, CourseForm, DepartmentForm
from .models import AcademicGroup, Course, Department


def is_methodist(user):
    return user.groups.filter(name='Методист').exists()


@login_required
def profile(request):
    return render(
        request,
        'profile.html',
        {
            'is_methodist': is_methodist(request.user)
        }
    )

@login_required
def dashboard_view(request):
    # 1. Карточки суммарных показателей
    total_courses = Course.objects.count()
    total_groups = AcademicGroup.objects.count()
    total_departments = Department.objects.count()
    total_users = User.objects.count()

    # 2. Дашборд №1: Распределение курсов по факультетам (используем 'courses')
    dept_courses = Department.objects.annotate(courses_count=Count('courses'))
    dept_course_labels = [dept.name for dept in dept_courses]
    dept_course_data = [dept.courses_count for dept in dept_courses]

    # 3. Дашборд №2: Количество групп по факультетам (используем 'groups')
    dept_groups = Department.objects.annotate(groups_count=Count('groups'))
    dept_group_labels = [dept.name for dept in dept_groups]
    dept_group_data = [dept.groups_count for dept in dept_groups]

    # 4. Дашборд №3: Разделение пользователей по ролям
    superusers_count = User.objects.filter(is_superuser=True).count()
    methodists_count = User.objects.filter(groups__name='Методист').distinct().count()
    students_count = total_users - superusers_count - methodists_count

    role_labels = ['Администраторы', 'Методисты', 'Студенты']
    role_data = [superusers_count, methodists_count, max(0, students_count)]

    context = {
        'is_methodist': is_methodist(request.user),
        # Метрики
        'total_courses': total_courses,
        'total_groups': total_groups,
        'total_departments': total_departments,
        'total_users': total_users,
        # Данные для графиков
        'dept_course_labels': dept_course_labels,
        'dept_course_data': dept_course_data,
        'dept_group_labels': dept_group_labels,
        'dept_group_data': dept_group_data,
        'role_labels': role_labels,
        'role_data': role_data,
    }
    return render(request, 'dashboard/dashboard.html', context)


# факультеты
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(
        request,
        'department_list.html',
        {
            'departments': departments,
            'is_methodist': is_methodist(request.user),
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление факультета',
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение факультета',
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': department,
            'title': 'Удаление факультета',
        }
    )


# группы
@login_required
def academic_group_list(request):
    groups = AcademicGroup.objects.select_related('department').all()
    return render(
        request,
        'academic_group_list.html',
        {
            'groups': groups,
            'is_methodist': is_methodist(request.user),
        }
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_create(request):
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm()
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление группы',
        }
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_update(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm(instance=group)
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение группы',
        }
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_delete(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('academic_group_list')
    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': group,
            'title': 'Удаление группы',
        }
    )


# курсы
@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(
        request,
        'course_list.html',
        {
            'courses': courses,
            'is_methodist': is_methodist(request.user),
        }
    )


@login_required
@user_passes_test(is_methodist)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление курса',
        }
    )


@login_required
@user_passes_test(is_methodist)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение курса',
        }
    )


@login_required
@user_passes_test(is_methodist)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': course,
            'title': 'Удаление курса',
        }
    )