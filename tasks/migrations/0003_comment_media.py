# Generated by Django 5.1 on 2024-08-29 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_alter_task_status_comment_commentdislike_commentlike_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='comments_media'),
        ),
    ]
