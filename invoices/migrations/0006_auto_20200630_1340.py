# Generated by Django 3.1b1 on 2020-06-30 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_invoice_invoice_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_status',
            field=models.IntegerField(blank=True, choices=[(1, 'Awaiting confirmation'), (2, 'Awaiting payment'), (3, 'Finished'), (4, 'Payment failed')], default=1, null=True),
        ),
    ]
