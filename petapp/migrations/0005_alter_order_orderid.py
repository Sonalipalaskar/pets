# Generated by Django 5.1.1 on 2024-10-16 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petapp', '0004_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderid',
            field=models.CharField(max_length=60),
        ),
    ]
