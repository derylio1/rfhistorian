# Generated by Django 4.0.5 on 2023-02-04 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_singletestresult_test_delete_teststatistic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcaseobject',
            name='name',
            field=models.CharField(max_length=200, verbose_name='test case name'),
        ),
    ]
