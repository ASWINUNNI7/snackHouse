# Generated by Django 5.1.1 on 2024-12-15 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0024_delete_booktable'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('table', models.CharField(max_length=4)),
                ('members', models.IntegerField(default=1)),
            ],
        ),
    ]
