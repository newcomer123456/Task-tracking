from django import forms
from tasks.models import Task, Comment

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        self.fields['due_date'].widget.attrs['class'] += ' datepicker'


class StatusTaskFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Всі'),
        ('todo', 'В планах'),
        ('in_progress', 'У процесі'),
        ('done', 'Виконано'),
    ] 

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Статус')

    def __init__(self, *args, **kwargs):
        super(StatusTaskFilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-control'})

class PriorityTaskFilterForm(forms.Form):
    PRIORITY_CHOICES = [
        ('', 'Всі'),
        ('low', 'Низька'),
        ('medium', 'Середня'),
        ('high', 'Висока'),
    ]

    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False, label='Важливість')

    def __init__(self, *args, **kwargs):
        super(PriorityTaskFilterForm, self).__init__(*args, **kwargs)
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'parent', 'media']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
            'parent': forms.HiddenInput(),
            'media': forms.FileInput(),
        }

class CommentUpdateForm(forms.ModelForm):
    new_media = forms.FileField(required=False, label="Новий файл")
    delete_media = forms.BooleanField(required=False, label="Видалити медіа")

    class Meta:
        model = Comment
        fields = ['content', 'new_media', 'delete_media']