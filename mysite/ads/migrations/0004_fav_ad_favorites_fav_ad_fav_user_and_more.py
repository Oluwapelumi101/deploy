# Generated by Django 4.0.7 on 2022-12-06 10:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0003_comment_ad_comments_comment_ad_comment_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fav',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='ad',
            name='favorites',
            field=models.ManyToManyField(related_name='favorite_ads', through='ads.Fav', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fav',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ads.ad'),
        ),
        migrations.AddField(
            model_name='fav',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='fav',
            unique_together={('ad', 'user')},
        ),
    ]
