# Seed nine demo products when the database is empty so category “Shop now”
# links (which map to products by id) resolve to real cart rows.

import base64

from django.core.files.base import ContentFile
from django.db import migrations

# 1×1 transparent PNG
TINY_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

SEED_NAMES = [
    'Teak Coffee Table',
    'Teak Chest of Drawer',
    'Teak Dressers & Mirrors',
    'Teak Wardrobes',
    'Teak TV Units',
    'Teak Sideboards',
    'Teak Bar Units & Stools',
    'Teak Bedside Table',
    'Teak Dining Coffee Table',
]


def seed(apps, schema_editor):
    Product = apps.get_model('furniture', 'Product')
    Category = apps.get_model('furniture', 'Category')
    if Product.objects.exists():
        return
    cat = Category.objects.create(name='Demo Catalog', slug='demo-catalog', is_active=True)
    cat.image.save('demo_cat.png', ContentFile(TINY_PNG), save=False)
    cat.save()
    for i, name in enumerate(SEED_NAMES):
        p = Product(
            category=cat,
            name=name,
            description='Demo furniture catalog item.',
            price='8000.00',
            stock=99,
        )
        p.image.save(f'seed_{i + 1}.png', ContentFile(TINY_PNG), save=False)
        p.save()


def unseed(apps, schema_editor):
    Product = apps.get_model('furniture', 'Product')
    Category = apps.get_model('furniture', 'Category')
    Product.objects.filter(category__slug='demo-catalog').delete()
    Category.objects.filter(slug='demo-catalog').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('furniture', '0003_order_payment_fields'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
