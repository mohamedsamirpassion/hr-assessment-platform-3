# Generated by Django 5.1.6 on 2025-02-26 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_question_is_auto_graded_alter_question_points_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='is_auto_graded',
            field=models.BooleanField(default=True, help_text='Whether this question is auto-graded or manually graded (e.g., MC/TF are auto, SA/UP are manual)'),
        ),
    ]
