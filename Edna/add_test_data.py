#!/usr/bin/env python
"""
Script pour ajouter des données de test à la base de données Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Edna.settings')
django.setup()

from core.models import Category, Product, Service, Actualite, Suject

# Nettoyer les anciennes données
Category.objects.all().delete()
Service.objects.all().delete()
Actualite.objects.all().delete()
Suject.objects.all().delete()

# Créer les catégories
cat_medical = Category.objects.create(name="Équipements médicaux")
cat_consumables = Category.objects.create(name="Consommables")
cat_lab = Category.objects.create(name="Laboratoire")

# Créer des produits
products_data = [
    {
        'name': 'Moniteur multiparamétrique MX-500',
        'description': 'Moniteur patient haute performance avec écran tactile 15" et connectivité sans fil.',
        'price': 20000,
        'category': cat_medical,
        'is_available': True,
    },
    {
        'name': 'Défibrillateur automatique DEA-300',
        'description': 'Défibrillateur externe automatique avec guidage vocal et analyse cardiaque intégrée.',
        'price': 15000,
        'category': cat_medical,
        'is_available': True,
    },
    {
        'name': 'Gants d\'examen nitrile (boîte de 100)',
        'description': 'Gants non stériles en nitrile, résistance chimique élevée, sans latex ni poudre.',
        'price': 12000,
        'category': cat_consumables,
        'is_available': True,
    },
]

for prod_data in products_data:
    Product.objects.create(**prod_data)

# Créer des services
services_data = [
    {
        'name': 'Consultation médicale',
        'description': 'Consultation professionnelle pour vos besoins biomédicaux',
    },
    {
        'name': 'Installation et formation',
        'description': 'Installation complète et formation du personnel sur nos équipements',
    },
    {
        'name': 'Maintenance et support',
        'description': 'Support technique 24/7 et maintenance préventive',
    },
]

for svc_data in services_data:
    Service.objects.create(**svc_data)

# Créer une actualité
Actualite.objects.create(
    name='Nouvelle gamme d\'équipements',
    description='Découvrez notre nouvelle gamme d\'équipements biomédicaux de dernière génération.',
    is_published=True,
    is_featured=True,
)

# Créer des sujets de contact
Suject.objects.create(name='Devis')
Suject.objects.create(name='Support technique')
Suject.objects.create(name='Commande')
Suject.objects.create(name='Partenariat')

print('✅ Données de test créées avec succès!')
