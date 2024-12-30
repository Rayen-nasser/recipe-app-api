# Generated by Django 3.2.25 on 2024-12-30 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20241230_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=1000),
        ),
    ]
