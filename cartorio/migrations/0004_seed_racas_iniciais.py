from django.db import migrations


RACAS_INICIAIS = [
    'Índio Gigante',
    'Rhode Island Red',
    'Plymouth Rock',
]


def criar_racas_iniciais(apps, schema_editor):
    Raca = apps.get_model('cartorio', 'Raca')
    for nome in RACAS_INICIAIS:
        Raca.objects.get_or_create(nome=nome)


def remover_racas_iniciais(apps, schema_editor):
    Raca = apps.get_model('cartorio', 'Raca')
    Raca.objects.filter(nome__in=RACAS_INICIAIS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('cartorio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_racas_iniciais, remover_racas_iniciais),
    ]