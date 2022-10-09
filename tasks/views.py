from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'tasks/home.html')

def signup(request):
    postdict = request.POST

    if request.method == 'GET':
        return render(request, 'tasks/signup.html', {
            'form': UserCreationForm
        })
    else:
        if postdict['password1'] == postdict['password2']:
            # Register user
            try:
                user = User.objects.create_user(
                    username=postdict['username'], password=postdict['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')  # name of the url tasks/
            except IntegrityError:
                return render(request, 'tasks/signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })
        return render(request, 'tasks/signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })

@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'tasks/create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'tasks/create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid Data'
            })
            
@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user= request.user)
        form = TaskForm(instance=task)
        return render(request, 'tasks/task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user= request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            task = get_object_or_404(Task, pk=task_id, user= request.user)
            form = TaskForm(request.POST, instance=task)
            return render(request, 'tasks/task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error updating the task'
            })
    
@login_required  # type: ignore
def complete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required  # type: ignore
def delete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'tasks/signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'tasks/signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')