# Generated by Django 2.1.7 on 2019-05-24 00:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cnonce',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nonce', models.CharField(db_index=True, max_length=300)),
                ('timestamp', models.DateTimeField()),
                ('created_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'db_table': 'nonce',
                'managed': False,
            },
        ),
    ]
