from django.contrib import admin
from tasks.models import Task, Comment, Like, Dislike, CommentDislike, CommentLike

# Register your models here.
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(CommentDislike)
admin.site.register(CommentLike)