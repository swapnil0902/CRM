# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm,TaskFilterForm

# List all tasks
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

    # Sorting
    sort_by = request.GET.get('sort_by', 'due_date')
    if sort_by in ['due_date', 'priority', 'status']:
        tasks = tasks.order_by(sort_by)

    return render(request, 'task/task_list.html', {'tasks': tasks, 'form': form})

# Create a new task
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'task/task_create.html', {'form': form})

# View task details
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'task/task_detail.html', {'task': task})

def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('task_list')
    return render(request, 'task/task_update.html', {'form': form})

def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'task/task_delete.html', {'task': task})
