from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
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

    def get_queryset(self):
        return Product.objects.filter(is_available=True).select_related('categorie')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similaires'] = Product.objects.filter(
            is_available=True, categorie=self.object.categorie
        ).exclude(pk=self.object.pk)[:3]
        return context


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

def parse_quantity(value, default=1):
    """Convertit une quantité saisie en entier, sans planter sur une valeur invalide."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def build_cart_items(request):
    """Construit les lignes du panier à partir de la session.
    Les produits supprimés ou indisponibles sont ignorés."""
    cart = get_cart(request)
    product_ids = [item['product_id'] for item in cart]
    products = Product.objects.filter(id__in=product_ids, is_available=True).select_related('categorie')
    product_dict = {p.id: p for p in products}
    cart_items = []
    total = 0
    for item in cart:
        product = product_dict.get(item['product_id'])
        if not product:
            continue
        subtotal = product.price * item['quantity']
        cart_items.append({'product': product, 'quantity': item['quantity'], 'subtotal': subtotal})
        total += subtotal
    return cart_items, total

def clear_cart(request):
    """Vide le panier."""
    request.session['cart'] = []
    request.session.modified = True
class CartView(TemplateView):
    template_name = 'core/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_items'], context['cart_total'] = build_cart_items(self.request)
        return context

class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_available=True)
        quantity = max(1, parse_quantity(request.POST.get('quantity')))
        add_to_cart(request, product.id, quantity)
        messages.success(request, f"« {product.name} » a été ajouté au panier.")
        next_url = request.META.get('HTTP_REFERER')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('produits')

class RemoveFromCartView(View):
    def post(self, request, product_id):
        remove_from_cart(request, product_id)
        return redirect('cart')

class UpdateCartView(View):
    def post(self, request, product_id):
        quantity = parse_quantity(request.POST.get('quantity'))
        update_cart_quantity(request, product_id, quantity)
        return redirect('cart')

class QuoteRequestView(CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'core/quote_form.html'
    success_url = reverse_lazy('quote_success')

    def dispatch(self, request, *args, **kwargs):
        # Une demande de devis sans produit n'a pas de sens : on renvoie au catalogue.
        if not build_cart_items(request)[0]:
            messages.info(request, "Votre panier est vide : ajoutez des produits avant de demander un devis.")
            return redirect('produits')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_items'], context['cart_total'] = build_cart_items(self.request)
        return context

    def form_valid(self, form):
        cart_items, _ = build_cart_items(self.request)
        quote = form.save()
        QuoteItem.objects.bulk_create([
            QuoteItem(quote=quote, product=item['product'], quantity=item['quantity'])
            for item in cart_items
        ])
        clear_cart(self.request)
        self.object = quote
        return redirect(self.get_success_url())

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