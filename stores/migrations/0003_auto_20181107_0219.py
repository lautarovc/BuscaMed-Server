# Generated by Django 2.1.2 on 2018-11-07 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_auto_20181107_0208'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productosportienda',
            old_name='medicina',
            new_name='producto',
        ),
    ]
