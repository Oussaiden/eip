from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0003_alter_devis_options_alter_dossier_options_and_more'),
        ('parametres', '0003_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='lignedevis',
            name='section',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lignes_devis',
                to='parametres.section',
                verbose_name='Section',
            ),
        ),
        migrations.AlterField(
            model_name='lignedevis',
            name='type',
            field=models.CharField(
                choices=[
                    ('article', 'Article catalogue'),
                    ('libre', 'Ligne libre'),
                    ('texte', 'Texte'),
                ],
                default='libre',
                max_length=20,
            ),
        ),
    ]
