from .models import Task
from .forms import TaskForm,TaskFilterForm
<<<<<<< HEAD
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
=======
from rest_framework.decorators import api_view
>>>>>>> 083b32bda1116cc553786e9c1786248944c78b42


#########################         #########################################
@login_required
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


########################         ##########################################
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = form.cleaned_data['assigned_to']
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'task/task_create.html', {'form': form})


########################         ##########################################
@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('task_list')
    return render(request, 'task/task_update.html', {'form': form})


########################         ##########################################
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'task/task_delete.html', {'task': task})

<<<<<<< HEAD
########################         ##########################################
=======





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

    # Sorting
    sort_by = request.GET.get('sort_by', 'due_date')
    if sort_by in ['due_date', 'priority', 'status']:
        tasks = tasks.order_by(sort_by)

    return render(request, 'task/company_task_list.html', {'tasks': tasks, 'form': form})



@login_required
def company_task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        return redirect('company_task_list')
    return render(request, 'task/company_task_update.html', {'form': form})


@api_view(['GET', 'DELETE'])
@login_required
def company_task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('company_task_list')
>>>>>>> 083b32bda1116cc553786e9c1786248944c78b42
