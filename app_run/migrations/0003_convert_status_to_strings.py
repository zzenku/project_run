from django.db import migrations


def convert_status_to_strings(apps, schema_editor):
    Run = apps.get_model('app_run', 'Run')
    for run in Run.objects.all():
        if run.status == '0' or run.status == 0:
            run.status = 'init'
        elif run.status == '1' or run.status == 1:
            run.status = 'in_progress'
        elif run.status == '2' or run.status == 2:
            run.status = 'finished'
        run.save()


class Migration(migrations.Migration):
    dependencies = [
        ('app_run', '0002_run_status'),
    ]

    operations = [
        migrations.RunPython(convert_status_to_strings),
    ]
