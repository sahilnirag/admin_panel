# Generated by Django 4.2.5 on 2024-01-15 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blink',
            name='blink_status',
            field=models.CharField(blank=True, choices=[('option1', 'Option 1'), ('option2', 'Option 2'), ('option3', 'Option 3')], max_length=20, null=True),
        ),
    ]