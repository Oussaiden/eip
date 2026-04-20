from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_article_prix_vente_ht'),
        ('parametres', '0003_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='sections',
            field=models.ManyToManyField(
                blank=True,
                related_name='articles',
                to='parametres.section',
                verbose_name='Sections',
            ),
        ),
    ]
