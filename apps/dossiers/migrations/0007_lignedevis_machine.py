import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_machine_add_fields'),
        ('dossiers', '0006_lignedevis_article_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lignedevis',
            name='machine',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lignes_devis',
                to='planning.machine',
            ),
        ),
        migrations.AlterField(
            model_name='lignedevis',
            name='type',
            field=models.CharField(
                choices=[
                    ('article', 'Article stock'),
                    ('service', 'Service'),
                    ('machine', 'Machine'),
                    ('libre', 'Ligne libre'),
                    ('texte', 'Texte'),
                ],
                default='libre',
                max_length=20,
            ),
        ),
    ]
