# Generated by Django 3.0.5 on 2020-04-24 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200424_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppinglistitem',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
