# Generated by Django 5.0.6 on 2024-08-21 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_remove_appointment_end_datetime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='title',
            field=models.CharField(default='Enter the Title', max_length=100),
        ),
    ]
