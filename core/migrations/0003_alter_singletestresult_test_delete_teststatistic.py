# Generated by Django 4.0.5 on 2023-02-04 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_teststatistic_remove_singletestresult_test_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singletestresult',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.testcaseobject'),
        ),
        migrations.DeleteModel(
            name='TestStatistic',
        ),
    ]
