# Generated by Django 4.2 on 2023-06-13 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_ticketmodel_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketmodel',
            name='send_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
