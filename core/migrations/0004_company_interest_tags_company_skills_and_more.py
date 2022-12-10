# Generated by Django 4.1.4 on 2022-12-10 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_studentprofile_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="interest_tags",
            field=models.ManyToManyField(
                blank=True, related_name="company_required_skills", to="core.tag"
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="skills",
            field=models.ManyToManyField(
                blank=True, related_name="company_scope", to="core.tag"
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="intext_match",
            field=models.CharField(
                default="",
                help_text="keywords separated by ';' symbol",
                max_length=1023,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="interest_tags",
            field=models.ManyToManyField(
                blank=True, related_name="user_required_skills", to="core.tag"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="skills",
            field=models.ManyToManyField(
                blank=True, related_name="user_skills", to="core.tag"
            ),
        ),
    ]