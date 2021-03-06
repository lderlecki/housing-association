# Generated by Django 3.1b1 on 2020-06-30 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_auto_20200629_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultServiceUsagePP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hot_water', models.DecimalField(decimal_places=2, default=0.07, max_digits=100)),
                ('cold_water', models.DecimalField(decimal_places=2, default=0.09, max_digits=100)),
                ('sewage', models.DecimalField(decimal_places=2, default=0.09, max_digits=100)),
                ('electricity', models.DecimalField(decimal_places=2, default=29.35, max_digits=100)),
                ('gas', models.DecimalField(decimal_places=2, default=0.09, max_digits=100)),
            ],
        ),
        migrations.CreateModel(
            name='Fees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hot_water', models.DecimalField(decimal_places=4, default=16.49, max_digits=100)),
                ('cold_water', models.DecimalField(decimal_places=4, default=4.29, max_digits=100)),
                ('sewage', models.DecimalField(decimal_places=4, default=4.38, max_digits=100)),
                ('electricity', models.DecimalField(decimal_places=4, default=0.621, max_digits=100)),
                ('gas', models.DecimalField(decimal_places=4, default=0.1175, max_digits=100)),
                ('repair_fund', models.DecimalField(decimal_places=4, default=0.09, max_digits=100)),
                ('service_charge_insulated', models.DecimalField(decimal_places=2, default=3.62, max_digits=100)),
                ('service_charge_non_insulated', models.DecimalField(decimal_places=2, default=3.33, max_digits=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='invoiceitems',
            name='invoice',
        ),
        migrations.AddField(
            model_name='invoice',
            name='services',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='invoices.invoiceitems'),
        ),
    ]
