# Generated by Django 5.1.6 on 2025-03-31 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_product', '0018_rename_idenifier_report_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='av_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='report',
            name='current_remainder',
            field=models.IntegerField(default=0),
        ),
    ]
