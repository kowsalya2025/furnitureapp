# Generated manually for checkout flow

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0002_category_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_ref',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
