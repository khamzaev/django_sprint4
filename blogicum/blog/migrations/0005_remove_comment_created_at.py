# Generated by Django 5.1.4 on 2025-01-12 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_comment_created_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="created_at",
        ),
    ]
