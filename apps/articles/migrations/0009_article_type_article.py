from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_article_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='type_article',
            field=models.CharField(
                choices=[('stock', 'Stock'), ('service', 'Service')],
                default='stock',
                max_length=10,
                verbose_name='Type',
            ),
        ),
    ]