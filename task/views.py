from .models import Task
from account.views import *
from .forms import TaskForm,TaskFilterForm
from .serializers import TaskListSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import IsAuthenticated,IsAdminUser, IsAuthenticatedOrReadOnly


######################### Tasks Details #########################################
class TaskList(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)

@login_required
@user_passes_test(is_User_or_Manager)
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    form = TaskFilterForm(request.GET or None)

    if form.is_valid():
        priority = form.cleaned_data.get('priority')
        status = form.cleaned_data.get('status')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if priority:
            tasks = tasks.filter(priority=priority)
        if status:
            tasks = tasks.filter(status=status)
        if start_date and end_date:
            tasks = tasks.filter(due_date__range=[start_date, end_date])
        elif start_date:
            tasks = tasks.filter(due_date__gte=start_date)
        elif end_date:
            tasks = tasks.filter(due_date__lte=end_date)

    sort_by = request.GET.get('sort_by', 'due_date')
    if sort_by in ['due_date', 'priority', 'status']:
        tasks = tasks.order_by(sort_by)

    return render(request, 'task/task_list.html', {'tasks': tasks, 'form': form})


######################## Creating Tasks ##########################################
User = get_user_model()
@user_passes_test(is_User_or_Manager)
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            if request.user.groups.filter(name='Staff').exists():
                task.assigned_to = request.user
                task.company = request.user.userprofile.company
            elif request.user.groups.filter(name='Account Manager').exists():
                task.company = request.user.userprofile.company
                assigned_to_id = request.POST.get('assigned_to')
                if assigned_to_id:
                    task.assigned_to = get_object_or_404(User, pk=assigned_to_id)
                else:
                    form.add_error('assigned_to', 'You must assign this task to a staff member.')
                    return render(request, 'task/task_create.html', {'form': form})
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)  

    return render(request, 'task/task_create.html', {'form': form})


########################  Updating Tasks #############################################
@login_required
@user_passes_test(is_User_or_Manager)
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task, user = request.user)
    if form.is_valid():
        form.save()
        return redirect('task_list')
    return render(request, 'task/task_update.html', {'form': form})


######################## Deleting Tasks ##########################################
@login_required
@user_passes_test(is_User_or_Manager)
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'task/task_delete.html', {'task': task})


######################## Tasks List(Company-Wise) ##########################################
@user_passes_test(is_Account_Manager)
def company_task_list(request):
    company = request.user.userprofile.company
    tasks = Task.objects.filter(assigned_to__userprofile__company=company)
    form = TaskFilterForm(request.GET or None)

    if form.is_valid():
        priority = form.cleaned_data.get('priority')
        status = form.cleaned_data.get('status')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if priority:
            tasks = tasks.filter(priority=priority)
        if status:
            tasks = tasks.filter(status=status)
        if start_date and end_date:
            tasks = tasks.filter(due_date__range=[start_date, end_date])
        elif start_date:
            tasks = tasks.filter(due_date__gte=start_date)
        elif end_date:
            tasks = tasks.filter(due_date__lte=end_date)

    sort_by = request.GET.get('sort_by', 'due_date')
    if sort_by in ['due_date', 'priority', 'status']:
        tasks = tasks.order_by(sort_by)

    return render(request, 'task/company_task_list.html', {'tasks': tasks, 'form': form})


######################## Update Tasks List(Company-Wise) ##########################################
@login_required
@user_passes_test(is_Account_Manager)
def company_task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        return redirect('company_task_list')
    return render(request, 'task/company_task_update.html', {'form': form})


######################## Delete Tasks List(Company-Wise) ##########################################
@api_view(['GET', 'DELETE'])
@login_required
@user_passes_test(is_Account_Manager)
def company_task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('company_task_list')

#################################### THE-END #######################################################