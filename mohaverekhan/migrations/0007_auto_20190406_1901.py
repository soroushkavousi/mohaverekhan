# Generated by Django 2.1.7 on 2019-04-06 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mohaverekhan', '0006_auto_20190406_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='texttag',
            name='accuracy',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='texttag',
            name='true_text_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mohaverekhan.TextTag'),
        ),
    ]