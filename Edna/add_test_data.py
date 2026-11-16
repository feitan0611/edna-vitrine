#!/usr/bin/env python
"""
Ajoute des données de démonstration à la base (développement uniquement).

Usage :  python add_test_data.py
Le script peut être relancé : il remplace les données de démo existantes.
"""
import os
import sys
from pathlib import Path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Edna.settings')
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.core.files import File  # noqa: E402

from core.models import Actualite, Categorie, Product, Service, Sujet  # noqa: E402

if not settings.DEBUG:
    sys.exit("Refusé : ce script ne doit pas tourner en production (DEBUG=False).")

STATIC_IMAGES = Path(__file__).resolve().parent / 'core' / 'static' / 'image'


def attach(instance, field, filename):
    """Copie une image du dossier static vers le champ image (dossier media)."""
    path = STATIC_IMAGES / filename
    if path.exists():
        with path.open('rb') as f:
            getattr(instance, field).save(filename.replace(' ', '-'), File(f), save=True)


# Nettoyage
Product.objects.all().delete()
Categorie.objects.all().delete()
Service.objects.all().delete()
Actualite.objects.all().delete()
Sujet.objects.all().delete()

# Catégories
cat_medical = Categorie.objects.create(nom="Équipements médicaux")
cat_consommables = Categorie.objects.create(nom="Consommables")
cat_labo = Categorie.objects.create(nom="Laboratoire")
cat_mobilier = Categorie.objects.create(nom="Mobilier médical")

# Produits
products_data = [
    ('Moniteur multiparamétrique MX-500', cat_medical, 20000, 'OIP.webp',
     'Moniteur patient haute performance avec écran tactile 15" et connectivité sans fil. '
     'Suivi ECG, SpO2, pression artérielle non invasive et température.'),
    ('Défibrillateur automatique DEA-300', cat_medical, 15000, 'OIP (1).webp',
     'Défibrillateur externe automatique avec guidage vocal et analyse cardiaque intégrée.'),
    ('Tensiomètre électronique TX-20', cat_medical, 8500, None,
     'Tensiomètre automatique au bras, mémoire 120 mesures, détection d\'arythmie.'),
    ('Gants d\'examen nitrile (boîte de 100)', cat_consommables, 12000, None,
     'Gants non stériles en nitrile, résistance chimique élevée, sans latex ni poudre.'),
    ('Masques chirurgicaux type IIR (boîte de 50)', cat_consommables, 4500, None,
     'Masques 3 plis, filtration bactérienne ≥ 98 %, résistants aux projections.'),
    ('Tubes de prélèvement sanguin EDTA (x100)', cat_labo, 9000, 'Sang.webp',
     'Tubes sous vide 4 ml avec anticoagulant EDTA K2 pour hématologie.'),
    ('Centrifugeuse de paillasse C-12', cat_labo, 185000, None,
     'Centrifugeuse 12 tubes, 4 000 tr/min, minuterie et verrouillage de sécurité.'),
    ('Microscope binoculaire LabView 400', cat_labo, 240000, None,
     'Microscope optique binoculaire, objectifs 4x à 100x, éclairage LED.'),
    ('Lit médicalisé électrique 3 fonctions', cat_mobilier, 650000, 'gros-lit.jpg',
     'Lit d\'hospitalisation électrique, relève-buste, relève-jambes et hauteur variable.'),
]

for name, cat, price, image, desc in products_data:
    product = Product.objects.create(name=name, categorie=cat, price=price, description=desc)
    if image:
        attach(product, 'image', image)

# Services
for name, desc in [
    ('Conseil et accompagnement', 'Étude de vos besoins et recommandation des équipements adaptés.'),
    ('Installation et formation', 'Installation complète et formation du personnel sur nos équipements.'),
    ('Maintenance et support', 'Support technique et maintenance préventive de votre parc.'),
]:
    Service.objects.create(name=name, description=desc)

# Actualités
articles = [
    ('Nouvelle gamme d\'équipements de monitoring', True, 'OIP.webp',
     'Découvrez notre nouvelle gamme de moniteurs patients de dernière génération, '
     'conçus pour les services d\'urgence et de réanimation.'),
    ('EDNA&SA équipe une clinique à Abidjan', False, 'gros-lit.jpg',
     'Nous avons livré et installé 20 lits médicalisés et l\'ensemble du matériel de monitoring '
     'd\'une nouvelle clinique privée.'),
    ('Bien choisir ses consommables de laboratoire', False, 'Sang.webp',
     'Tubes, réactifs, gants : nos conseils pour sécuriser vos prélèvements et vos analyses.'),
    ('Formation : utilisation du défibrillateur', False, None,
     'Retour sur notre session de formation aux gestes de premiers secours et à l\'utilisation du DEA.'),
]
for name, featured, image, desc in articles:
    article = Actualite.objects.create(name=name, description=desc, is_published=True, is_featured=featured)
    if image:
        attach(article, 'image', image)

# Sujets de contact
for name in ['Devis', 'Support technique', 'Commande', 'Partenariat']:
    Sujet.objects.create(name=name)

# Compte administrateur de démo
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('👤 Superutilisateur créé : admin / admin (développement uniquement)')

print(f'✅ Données de test créées : {Product.objects.count()} produits, '
      f'{Categorie.objects.count()} catégories, {Actualite.objects.count()} actualités.')
