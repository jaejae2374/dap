# Generated by Django 4.0.5 on 2022-07-23 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_mentee_tier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentee',
            name='tier',
            field=models.CharField(choices=[('GM', 'Grand-Master'), ('M', 'Master'), ('P', 'Pletinum'), ('G', 'Gold'), ('S', 'Silver'), ('B', 'Bronze'), ('U', 'Unranked')], default='Unranked', max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(max_length=10),
        ),
    ]
