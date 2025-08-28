from django.db import migrations

def add_specializations(apps, schema_editor):
    Specialization = apps.get_model('doctor', 'Specialization')
    specializations = [
        'Diabetes',
        'Neurology',
        'Gastroenterology',
        'Dermatology',
        'Orthopedic'
    ]
    for specialization in specializations:
        Specialization.objects.create(name=specialization)

class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_specializations),
    ]