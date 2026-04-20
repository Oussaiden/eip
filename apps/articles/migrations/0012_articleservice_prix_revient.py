from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_delete_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleservice',
            name='prix_revient',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Prix de revient'),
        ),
    ]