from django.shortcuts import render
from django.urls import reverse_lazy
from tasks import models
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from tasks.forms import TaskForm, StatusTaskFilterForm, PriorityTaskFilterForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.mixins import UserIsOwnerMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect


class TaskListView(ListView):
    model = models.Task
    context_object_name = 'tasks'
    template_name = 'tasks/tasks_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status', '')
        priority = self.request.GET.get('priority', '')
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks_with_likes_dislikes = []
        for task in context['tasks']:
            task.likes_count = task.likes.count()  # Використовуємо related_name 'likes'
            task.dislikes_count = task.dislikes.count()  # Використовуємо related_name 'dislikes'
            tasks_with_likes_dislikes.append(task)
        context["tasks"] = tasks_with_likes_dislikes
        context["status_form"] = StatusTaskFilterForm(self.request.GET)
        context["priority_form"] = PriorityTaskFilterForm(self.request.GET)
        return context
class TaskDetailView(DetailView):
    model = models.Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = models.Comment.objects.filter(task=self.object, parent=None)
        context['comment_form'] = CommentForm()
        context['likes'] = models.Like.objects.filter(task=self.object).count()
        context['dislikes'] = models.Dislike.objects.filter(task=self.object).count()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'add_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.task = self.object
                comment.author = request.user
                parent_id = request.POST.get('parent')
                if parent_id:
                    comment.parent = get_object_or_404(models.Comment, id=parent_id)
                comment.save()
            return self.render_to_response(self.get_context_data())

        elif 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            if comment.author == request.user:
                comment.delete()
            return self.render_to_response(self.get_context_data())

        elif 'like_task' in request.POST:
            models.Like.objects.get_or_create(user=request.user, task=self.object)
            models.Dislike.objects.filter(user=request.user, task=self.object).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'dislike_task' in request.POST:
            models.Dislike.objects.get_or_create(user=request.user, task=self.object)
            models.Like.objects.filter(user=request.user, task=self.object).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'remove_like' in request.POST:
            models.Like.objects.filter(user=request.user, task=self.object).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'remove_dislike' in request.POST:
            models.Dislike.objects.filter(user=request.user, task=self.object).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        return self.render_to_response(self.get_context_data())

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    template_name = 'tasks/task_form.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks:task-list')
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
    
class TaskCompleteView(LoginRequiredMixin, UserIsOwnerMixin, View):
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = 'done'
        task.save()
        return HttpResponseRedirect(reverse_lazy('tasks:task-list'))
    
    def get_object(self):
        task_id = self.kwargs.get('pk')
        return get_object_or_404(models.Task, pk=task_id)
     
class TaskUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    model = models.Task
    form_class = TaskForm
    template_name = 'tasks/task_update_form.html'
    success_url = reverse_lazy('tasks:task-list')

class TaskDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    model = models.Task
    success_url = reverse_lazy('tasks:task-list')
    template_name = 'tasks/task_delete_confirmation.html'

