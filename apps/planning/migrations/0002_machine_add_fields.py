from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='machine', name='reference', field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='machine', name='description', field=models.TextField(blank=True)),
        migrations.AddField(model_name='machine', name='format_min_largeur', field=models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='Larg. min (mm)')),
        migrations.AddField(model_name='machine', name='format_min_hauteur', field=models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='Haut. min (mm)')),
        migrations.AddField(model_name='machine', name='format_max_largeur', field=models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='Larg. max (mm)')),
        migrations.AddField(model_name='machine', name='format_max_hauteur', field=models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='Haut. max (mm)')),
        migrations.AddField(model_name='machine', name='nb_couleurs', field=models.PositiveIntegerField(default=4, verbose_name='Nb couleurs')),
        migrations.AddField(model_name='machine', name='vitesse_max', field=models.DecimalField(decimal_places=1, default=0, max_digits=8, verbose_name='Vitesse max (t/min)')),
        migrations.AddField(model_name='machine', name='recto_verso', field=models.BooleanField(default=False, verbose_name='Recto-verso')),
        migrations.AddField(model_name='machine', name='vitesse_recto_verso', field=models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='Vitesse R/V (t/min)')),
        migrations.AddField(model_name='machine', name='temps_mise_en_oeuvre', field=models.DecimalField(decimal_places=1, default=0, max_digits=6, verbose_name='Mise en œuvre (min)')),
        migrations.AddField(model_name='machine', name='temps_calage', field=models.DecimalField(decimal_places=1, default=0, max_digits=6, verbose_name='Calage (min)')),
        migrations.AddField(model_name='machine', name='temps_nettoyage', field=models.DecimalField(decimal_places=1, default=0, max_digits=6, verbose_name='Nettoyage (min)')),
        migrations.AddField(model_name='machine', name='cout_nrj_heure', field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Coût NRJ (XPF/h)')),
        migrations.AddField(model_name='machine', name='cout_amortissement_heure', field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Coût amortissement (XPF/h)')),
        migrations.AddField(model_name='machine', name='cout_entretien_heure', field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Coût entretien (XPF/h)')),
        migrations.AddField(model_name='machine', name='taux_gache', field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Taux de gâche (%)')),
        migrations.AlterField(model_name='machine', name='nom', field=models.CharField(max_length=255)),
        migrations.AlterUniqueTogether(name='machine', unique_together={('reference',)}),
    ]
