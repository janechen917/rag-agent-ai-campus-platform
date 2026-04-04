from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_service', '0005_debatematch_debateround_debatebadge'),
    ]

    operations = [
        migrations.AddField(
            model_name='debatematch',
            name='is_hidden',
            field=models.BooleanField(default=False, verbose_name='是否从最近战绩隐藏'),
        ),
    ]
