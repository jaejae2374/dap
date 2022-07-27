# Generated by Django 4.0.5 on 2022-07-23 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_mentee_description_alter_mentor_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mentor',
            name='major',
        ),
        migrations.AddField(
            model_name='mentor',
            name='genre',
            field=models.ManyToManyField(related_name='mentors', to='user.genre'),
        ),
        migrations.AlterField(
            model_name='mentee',
            name='genre',
            field=models.ManyToManyField(related_name='mentees', to='user.genre'),
        ),
    ]
