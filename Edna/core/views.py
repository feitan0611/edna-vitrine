from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, CreateView, ListView, View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from .models import Product, Actualite, Categorie, QuoteRequest, QuoteItem
from .forms import SignUpForm, ContactForm, QuoteRequestForm
from django.db import models

class IndexView(TemplateView):
    template_name = 'core/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prods'] = Product.objects.filter(is_available=True)\
            .select_related('categorie')[:3]
        context['blog_posts'] = Actualite.objects.filter(is_published=True)[:3]
        return context

class DetailViewProduct(DetailView):
    template_name = 'core/product_detail.html'
    model = Product
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class ContactView(CreateView):
    form_class = ContactForm
    template_name = 'core/contact.html'
    success_url = reverse_lazy('contact_success')

class ContactSuccessView(TemplateView):
    template_name = 'core/contact_success.html'

class ProductListView(ListView):
    model = Product
    template_name = 'core/produits.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        # On garde le filtrage de base
        queryset = Product.objects.filter(is_available=True).select_related('categorie')
        
        # Filtrage par catégorie
        categorie_slug = self.request.GET.get('categorie')
        if categorie_slug:
            queryset = queryset.filter(categorie__slug=categorie_slug)
        
        # Tri
        tri = self.request.GET.get('tri')
        ordres = {
            'prix_croissant': 'price',
            'prix_decroissant': '-price',
            'nouveautes': '-created_at'
        }
        # On applique le tri s'il existe, sinon un tri par défaut (important pour la pagination stable)
        return queryset.order_by(ordres.get(tri, '-id'))

    def get_context_data(self, **kwargs):
        # On appelle le parent en premier
        context = super().get_context_data(**kwargs)
        
        # 1. Optimisation du comptage total : 
        # Le Paginator a déjà calculé le count. On le récupère sans refaire de requête SQL.
        context['total_produits'] = context['paginator'].count
        
        # 2. Récupération des catégories
        # Petit conseil : utilise distinct() si tu as des doutes sur les jointures
        context['categories'] = Categorie.objects.annotate(
            nb_produits=models.Count(
                'produits', 
                filter=models.Q(produits__is_available=True)
            )
        )
        
        context['categorie_active'] = self.request.GET.get('categorie', '')
        context['tri_active'] = self.request.GET.get('tri', 'pertinence')
        
        return context


def get_cart(request):
    """Récupère le panier depuis la session."""
    return request.session.get('cart', [])

def add_to_cart(request, product_id, quantity=1):
    """Ajoute un produit au panier (incrémente la quantité si déjà présent)."""
    cart = request.session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})
    request.session['cart'] = cart
    request.session.modified = True

def remove_from_cart(request, product_id):
    """Retire un produit du panier."""
    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    request.session['cart'] = cart
    request.session.modified = True

def update_cart_quantity(request, product_id, quantity):
    """Met à jour la quantité d'un produit (supprime si quantité <= 0)."""
    if quantity <= 0:
        remove_from_cart(request, product_id)
        return
    cart = request.session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    request.session['cart'] = cart
    request.session.modified = True

def clear_cart(request):
    """Vide le panier."""
    request.session['cart'] = []
    request.session.modified = True
class CartView(TemplateView):
    template_name = 'core/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        if not cart:
            context['cart_items'] = []
            context['cart_total'] = 0
            return context
        
        product_ids = [item['product_id'] for item in cart]
        products = Product.objects.filter(id__in=product_ids).select_related('categorie')
        # Créer un dictionnaire pour accès rapide
        product_dict = {p.id: p for p in products}
        
        cart_items = []
        total = 0
        for item in cart:
            product = product_dict.get(item['product_id'])
            if not product:
                continue  # produit supprimé ?
            subtotal = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
            })
            total += subtotal
        context['cart_items'] = cart_items
        context['cart_total'] = total
        return context
class AddToCartView(View):
    def post(self, request, product_id):
        quantity = int(request.POST.get('quantity', 1))
        add_to_cart(request, product_id, quantity)
        return redirect(request.META.get('HTTP_REFERER', 'produits'))

class RemoveFromCartView(View):
    def post(self, request, product_id):
        remove_from_cart(request, product_id)
        return redirect('cart')

class UpdateCartView(View):
    def post(self, request, product_id):
        quantity = int(request.POST.get('quantity', 1))
        update_cart_quantity(request, product_id, quantity)
        return redirect('cart')

class QuoteRequestView(CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'core/quote_form.html'
    success_url = reverse_lazy('quote_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le résumé du panier au contexte
        cart = get_cart(self.request)
        product_ids = [item['product_id'] for item in cart]
        products = Product.objects.filter(id__in=product_ids)
        cart_items = []
        total = 0
        for item in cart:
            product = products.get(id=item['product_id'])
            subtotal = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
            })
            total += subtotal
        context['cart_items'] = cart_items
        context['cart_total'] = total
        return context
    
    def form_valid(self, form):
        # Sauvegarder la demande de devis
        quote = form.save()
        # Récupérer le panier
        cart = get_cart(self.request)
        for item in cart:
            QuoteItem.objects.create(
                quote=quote,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
        # Vider le panier
        clear_cart(self.request)
        return super().form_valid(form)

class QuoteSuccessView(TemplateView):
    template_name = 'core/quote_success.html'

class ActualiteListView(ListView):
    model = Actualite
    template_name = 'core/actualite.html'
    context_object_name = 'actualites'
    paginate_by = 9

    def get_queryset(self):
        return Actualite.objects.filter(is_published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured = Actualite.objects.filter(is_published=True, is_featured=True).first()
        if not featured:
            featured = self.get_queryset().first()
        context['featured_article'] = featured
        # Articles récents (exclure le vedette)
        recent = self.get_queryset()
        if featured:
            recent = recent.exclude(pk=featured.pk)
        context['recent_articles'] = recent[:6]
        # Vidéos (articles avec une URL vidéo non vide)
        context['videos'] = self.get_queryset().exclude(video_url='').exclude(video_url=None)[:3]
        return context

class ActualiteDetailView(DetailView):
    model = Actualite
    template_name = 'core/actualite_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Actualite.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['galerie'] = self.object.galerie.all()
        context['autres_articles'] = Actualite.objects.filter(is_published=True)\
            .exclude(pk=self.object.pk)[:3]
        return context