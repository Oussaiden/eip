import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0002_numerotationdocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('libelle', models.CharField(max_length=100, unique=True)),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Section devis',
                'verbose_name_plural': 'Sections devis',
                'ordering': ['ordre', 'libelle'],
            },
        ),
    ]
