# Generated by Django 4.1.4 on 2022-12-10 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_alter_tag_intext_match_studentrequest"),
    ]

    operations = [
        migrations.RenameField(
            model_name="project",
            old_name="responses",
            new_name="team",
        ),
        migrations.AlterField(
            model_name="studentrequest",
            name="state",
            field=models.CharField(
                default="open",
                max_length=15,
                verbose_name=[
                    ("open", "Open"),
                    ("accepted", "Accepted"),
                    ("rejected", "Rejected"),
                ],
            ),
        ),
    ]