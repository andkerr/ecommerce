# Generated by Django 3.2.6 on 2021-08-18 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0028_alter_listing_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to=None, verbose_name='Upload an Image (optional)'),
        ),
    ]