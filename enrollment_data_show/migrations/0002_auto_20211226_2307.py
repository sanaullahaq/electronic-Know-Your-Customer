# Generated by Django 3.2.9 on 2021-12-26 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment_data_show', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='economicinfo',
            name='bank_account_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='economicinfo',
            name='nid_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='economicinfo',
            name='student_annual_income',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='economicinfo',
            name='student_occupation',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='address',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='bloodGroup',
            field=models.CharField(max_length=3),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='date_of_birth',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='fathers_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='fathers_occupation',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='fathers_phone_number',
            field=models.CharField(max_length=14),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='gender',
            field=models.CharField(max_length=6),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='marital_status',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='mothers_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='mothers_occupation',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='mothers_phone_number',
            field=models.CharField(max_length=14),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='phone_number',
            field=models.CharField(max_length=14),
        ),
    ]