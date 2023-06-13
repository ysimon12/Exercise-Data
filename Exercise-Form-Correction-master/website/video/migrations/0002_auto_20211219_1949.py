# Generated by Django 3.2.8 on 2021-12-20 00:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoseTimeSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_video', models.FileField(blank=True, upload_to='original')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.TextField(default='Unknown')),
                ('label', models.TextField(default='Unknown')),
                ('feedback', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='formcheck',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formcheck',
            name='prediction',
            field=models.TextField(default='Unknown'),
        ),
        migrations.AddField(
            model_name='formcheck',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='formcheck',
            name='nearest1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='near1+', to='video.posetimeseries'),
        ),
        migrations.AddField(
            model_name='formcheck',
            name='nearest2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='near2+', to='video.posetimeseries'),
        ),
        migrations.AddField(
            model_name='formcheck',
            name='nearest3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='near3+', to='video.posetimeseries'),
        ),
    ]
