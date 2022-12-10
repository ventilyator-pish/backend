# Generated by Django 4.1.4 on 2022-12-10 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_company_interest_tags_company_skills_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="intext_match",
            field=models.CharField(
                blank=True,
                help_text="keywords separated by ';' symbol",
                max_length=1023,
            ),
        ),
        migrations.CreateModel(
            name="StudentRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("datetime", models.DateTimeField(auto_now=True)),
                (
                    "state",
                    models.CharField(
                        max_length=15,
                        verbose_name=[
                            ("open", "Open"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                        ],
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.company"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.studentprofile",
                    ),
                ),
            ],
        ),
    ]
