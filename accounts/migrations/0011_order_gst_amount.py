# Generated by Django 5.1.5 on 2025-03-23 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='gst_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
