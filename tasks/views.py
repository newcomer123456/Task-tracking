from django.shortcuts import render
from django.urls import reverse_lazy
from tasks import models
from django.views.generic import ListView, DetailView, CreateView
from tasks.forms import TaskForm

class TaskListView(ListView):
    model = models.Task
    context_object_name = 'tasks'
    template_name = 'tasks/tasks_list.html'

class TaskDetailView(DetailView):
    model = models.Task
    context_object_name = 'task'
    template_name = 'tasks/task_detail.html'

class TaskCreateView(CreateView):
    model = models.Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks:task-list')