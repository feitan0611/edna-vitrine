from django.test import TestCase
from django.urls import reverse

from .models import Actualite, Categorie, ContactMessage, Product, QuoteItem, QuoteRequest


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Categorie.objects.create(nom="Laboratoire")
        cls.product = Product.objects.create(
            name="Centrifugeuse C-12", description="Centrifugeuse", price=1000, categorie=cls.cat)
        cls.hidden = Product.objects.create(
            name="Ancien modèle", description="Retiré", price=500, categorie=cls.cat, is_available=False)
        cls.article = Actualite.objects.create(name="Nouvelle gamme", description="Texte", is_published=True)
        Actualite.objects.create(name="Brouillon", description="Texte", is_published=False)

    def add(self, product, quantity=1):
        return self.client.post(reverse('add_to_cart', args=[product.id]), {'quantity': quantity})


class PagesTests(BaseTestCase):
    def test_pages_publiques(self):
        for name in ['index', 'produits', 'services', 'a_propos', 'actualite', 'contact',
                     'cart', 'login', 'signup', 'contact_success', 'quote_success']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_accueil_affiche_les_produits_disponibles(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.hidden.name)

    def test_detail_produit(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, self.product.name)

    def test_detail_produit_indisponible_404(self):
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)

    def test_filtre_categorie(self):
        autre = Categorie.objects.create(nom="Consommables")
        Product.objects.create(name="Gants nitrile", description="x", price=10, categorie=autre)
        response = self.client.get(reverse('produits'), {'categorie': autre.slug})
        self.assertContains(response, "Gants nitrile")
        self.assertNotContains(response, self.product.name)

    def test_article_a_la_une_affiche_son_image(self):
        self.article.is_featured = True
        self.article.image = 'actualite_images/test.jpg'
        self.article.save()
        response = self.client.get(reverse('actualite'))
        self.assertContains(response, '/media/actualite_images/test.jpg')

    def test_actualites_publiees_seulement(self):
        self.assertEqual(self.client.get(self.article.get_absolute_url()).status_code, 200)
        brouillon = Actualite.objects.get(name="Brouillon")
        self.assertEqual(self.client.get(brouillon.get_absolute_url()).status_code, 404)


class CartTests(BaseTestCase):
    def test_ajout_et_increment(self):
        self.add(self.product, 2)
        self.add(self.product, 3)
        self.assertEqual(self.client.session['cart'], [{'product_id': self.product.id, 'quantity': 5}])

    def test_quantite_invalide_ne_plante_pas(self):
        response = self.add(self.product, 'abc')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['cart'][0]['quantity'], 1)

    def test_produit_inexistant_ou_indisponible_404(self):
        self.assertEqual(self.client.post(reverse('add_to_cart', args=[9999])).status_code, 404)
        self.assertEqual(self.add(self.hidden).status_code, 404)

    def test_redirection_externe_refusee(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]),
                                    HTTP_REFERER='https://evil.example.com/')
        self.assertRedirects(response, reverse('produits'))

    def test_mise_a_jour_et_suppression(self):
        self.add(self.product)
        self.client.post(reverse('update_cart', args=[self.product.id]), {'quantity': 4})
        self.assertEqual(self.client.session['cart'][0]['quantity'], 4)
        self.client.post(reverse('update_cart', args=[self.product.id]), {'quantity': 0})
        self.assertEqual(self.client.session['cart'], [])

    def test_panier_ignore_produit_supprime(self):
        temp = Product.objects.create(name="Temp", description="x", price=1, categorie=self.cat)
        self.add(self.product, 2)
        self.add(temp)
        temp.delete()
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_total'], 2000)


class QuoteTests(BaseTestCase):
    data = {'nom': 'Konan', 'prenom': 'Awa', 'email': 'awa@example.com'}

    def test_devis_panier_vide_redirige(self):
        response = self.client.get(reverse('quote_request'))
        self.assertRedirects(response, reverse('produits'))

    def test_devis_cree_les_lignes_et_vide_le_panier(self):
        self.add(self.product, 3)
        response = self.client.post(reverse('quote_request'), self.data)
        self.assertRedirects(response, reverse('quote_success'))
        quote = QuoteRequest.objects.get()
        self.assertEqual(list(quote.items.values_list('product_id', 'quantity')), [(self.product.id, 3)])
        self.assertEqual(self.client.session['cart'], [])

    def test_devis_avec_produit_supprime(self):
        temp = Product.objects.create(name="Temp", description="x", price=1, categorie=self.cat)
        self.add(self.product)
        self.add(temp)
        temp.delete()
        self.assertEqual(self.client.get(reverse('quote_request')).status_code, 200)
        self.client.post(reverse('quote_request'), self.data)
        self.assertEqual(QuoteItem.objects.count(), 1)


class ContactTests(TestCase):
    def test_envoi_message(self):
        response = self.client.post(reverse('contact'), {
            'prenom': 'Awa', 'nom': 'Konan', 'email': 'awa@example.com',
            'sujet': 'devis', 'message': 'Bonjour',
        })
        self.assertRedirects(response, reverse('contact_success'))
        self.assertEqual(ContactMessage.objects.count(), 1)
