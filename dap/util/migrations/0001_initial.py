# Generated by Django 4.0.5 on 2022-07-29 05:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('detail', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=20, null=True)),
                ('district', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocationImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(null=True, upload_to='academy/<django.db.models.fields.CharField>/location')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='util.location')),
            ],
        ),
    ]
