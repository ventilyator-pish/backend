# Generated by Django 4.1.4 on 2022-12-11 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_studentrequest_initiator"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentrequest",
            name="project",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.project",
            ),
        ),
        migrations.AlterField(
            model_name="studentrequest",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.company",
            ),
        ),
    ]
