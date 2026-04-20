import django.db.models.deletion
import uuid
from django.db import migrations, models


def migrate_articles_to_new_models(apps, schema_editor):
    Article = apps.get_model('articles', 'Article')
    ArticleStock = apps.get_model('articles', 'ArticleStock')
    ArticleService = apps.get_model('articles', 'ArticleService')

    for article in Article.objects.all():
        if getattr(article, 'type_article', 'stock') == 'service':
            svc = ArticleService(
                id=article.id,
                reference=article.reference,
                designation=article.designation,
                categorie=article.categorie,
                unite=article.unite,
                tgc_vente=article.tgc_vente,
                prix_vente_ht=article.prix_vente_ht,
                notes=article.notes,
                actif=article.actif,
            )
            svc.save()
            for section in article.sections.all():
                svc.sections.add(section)
        else:
            stk = ArticleStock(
                id=article.id,
                reference=article.reference,
                designation=article.designation,
                categorie=article.categorie,
                unite=article.unite,
                tgc_achat=article.tgc_achat,
                tgc_vente=article.tgc_vente,
                prix_vente_ht=article.prix_vente_ht,
                stock_actuel=article.stock_actuel,
                seuil_minimum=article.seuil_minimum,
                valeur_stock=article.valeur_stock,
                pru_moyen=article.pru_moyen,
                notes=article.notes,
                actif=article.actif,
            )
            stk.save()
            for section in article.sections.all():
                stk.sections.add(section)


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_article_type_article'),
        ('parametres', '0004_alter_section_options'),
    ]

    operations = [
        # 1. Create new models first
        migrations.CreateModel(
            name='ArticleService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('designation', models.CharField(max_length=255)),
                ('prix_vente_ht', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Prix de vente HT')),
                ('notes', models.TextField(blank=True)),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles_service', to='parametres.categorie')),
                ('sections', models.ManyToManyField(blank=True, related_name='articles_service', to='parametres.section', verbose_name='Sections')),
                ('tgc_vente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articles_service_vente', to='parametres.tgc', verbose_name='TGC vente')),
                ('unite', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles_service', to='parametres.unite')),
            ],
            options={
                'verbose_name': 'Article service',
                'verbose_name_plural': 'Articles service',
                'ordering': ['categorie__libelle', 'designation'],
            },
        ),
        migrations.CreateModel(
            name='ArticleStock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('designation', models.CharField(max_length=255)),
                ('prix_vente_ht', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Prix de vente HT')),
                ('stock_actuel', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('seuil_minimum', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('valeur_stock', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('pru_moyen', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('actif', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles_stock', to='parametres.categorie')),
                ('sections', models.ManyToManyField(blank=True, related_name='articles_stock', to='parametres.section', verbose_name='Sections')),
                ('tgc_achat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articles_stock_achat', to='parametres.tgc', verbose_name='TGC achat')),
                ('tgc_vente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articles_stock_vente', to='parametres.tgc', verbose_name='TGC vente')),
                ('unite', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles_stock', to='parametres.unite')),
            ],
            options={
                'verbose_name': 'Article stock',
                'verbose_name_plural': 'Articles stock',
                'ordering': ['categorie__libelle', 'designation'],
            },
        ),
        # 2. Copy data from Article to new models
        migrations.RunPython(migrate_articles_to_new_models, migrations.RunPython.noop),
        # 3. Update FKs to point to ArticleStock
        migrations.AlterField(
            model_name='articlefournisseur',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fournisseurs', to='articles.articlestock'),
        ),
        migrations.AlterField(
            model_name='mouvementstock',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mouvements', to='articles.articlestock'),
        ),
        # 4. Remove old fields from Article (it will be deleted in 0011)
        migrations.RemoveField(
            model_name='article',
            name='categorie',
        ),
        migrations.RemoveField(
            model_name='article',
            name='sections',
        ),
        migrations.RemoveField(
            model_name='article',
            name='tgc_achat',
        ),
        migrations.RemoveField(
            model_name='article',
            name='tgc_vente',
        ),
        migrations.RemoveField(
            model_name='article',
            name='unite',
        ),
    ]
