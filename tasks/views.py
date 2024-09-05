from django.forms import BaseModelForm
from django.shortcuts import render
from django.urls import reverse_lazy
from tasks import models
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView
from tasks.forms import TaskForm, StatusTaskFilterForm, PriorityTaskFilterForm, CommentForm, CommentUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.mixins import UserIsOwnerMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login



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
            task.comments_count = task.comments.count()
            tasks_with_likes_dislikes.append(task)
        context["tasks"] = tasks_with_likes_dislikes
        context["status_form"] = StatusTaskFilterForm(self.request.GET)
        context["priority_form"] = PriorityTaskFilterForm(self.request.GET)
        return context
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = models.Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = models.Comment.objects.filter(task=self.object, parent=None)
        for comment in comments:    
            comment.has_liked = models.CommentLike.objects.filter(user=self.request.user, comment=comment).exists()
            comment.has_disliked = models.CommentDislike.objects.filter(user=self.request.user, comment=comment).exists()
            comment.likes_count = models.CommentLike.objects.filter(comment=comment).count()
            comment.dislikes_count = models.CommentDislike.objects.filter(comment=comment).count()

        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['comment_update_form'] = CommentUpdateForm()
        context['likes'] = models.Like.objects.filter(task=self.object).count()
        context['dislikes'] = models.Dislike.objects.filter(task=self.object).count()
        context['has_liked'] = models.Like.objects.filter(user=self.request.user, task=self.object).exists()
        context['has_disliked'] = models.Dislike.objects.filter(user=self.request.user, task=self.object).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'add_comment' in request.POST:
            form = CommentForm(request.POST, request.FILES)
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
        
        elif 'update_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            if comment.author == request.user:
                form = CommentUpdateForm(request.POST, request.FILES, instance=comment)
                if form.is_valid():
                    # Видалення поточного медіа-файлу, якщо обрано
                    if form.cleaned_data.get('delete_media') and comment.media:
                        comment.media.delete()
                        comment.media = None
            
                # Додавання нового медіа-файлу
                    if form.cleaned_data.get('new_media'):
                        comment.media = form.cleaned_data['new_media']
            
                    form.save()
                    return redirect('tasks:task-detail', pk=comment.task.pk)


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

        elif 'like_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            models.CommentLike.objects.get_or_create(user=request.user, comment=comment)
            models.CommentDislike.objects.filter(user=request.user, comment=comment).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'dislike_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            models.CommentDislike.objects.get_or_create(user=request.user, comment=comment)
            models.CommentLike.objects.filter(user=request.user, comment=comment).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'remove_like_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            models.CommentLike.objects.filter(user=request.user, comment=comment).delete()
            return redirect('tasks:task-detail', pk=self.object.pk)

        elif 'remove_dislike_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(models.Comment, id=comment_id)
            models.CommentDislike.objects.filter(user=request.user, comment=comment).delete()
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

class CustomLoginView(LoginView):
    template_name = 'tasks/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page='tasks:login'

class RegisterView(CreateView):
    template_name = 'tasks/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('tasks:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
