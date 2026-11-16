from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from .views import ( IndexView, DetailViewProduct, SignUpView, ContactView, ContactSuccessView, ProductListView,
                    QuoteRequestView, CartView, AddToCartView, RemoveFromCartView, UpdateCartView, QuoteSuccessView,
                    ActualiteListView, ActualiteDetailView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('product/<slug:slug>/', DetailViewProduct.as_view(), name='product_detail'),
    path('produits/', ProductListView.as_view(), name='produits'),  # seule entrée pour produits

    # static pages
    path('services/', TemplateView.as_view(template_name='core/services.html'), name='services'),
    path('a-propos/', TemplateView.as_view(template_name='core/a_propos.html'), name='a_propos'),
    path('actualites/', ActualiteListView.as_view(), name='actualite'),
    path('actualites/<slug:slug>/', ActualiteDetailView.as_view(), name='actualite_detail'),

    # contact
    path('contact/', ContactView.as_view(), name='contact'),
    path('contact/merci/', ContactSuccessView.as_view(), name='contact_success'),

    # auth
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),

    path('panier/', CartView.as_view(), name='cart'),
    path('panier/ajouter/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('panier/supprimer/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('panier/mettre-a-jour/<int:product_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('demande-devis/', QuoteRequestView.as_view(), name='quote_request'),
    path('demande-devis/merci/', QuoteSuccessView.as_view(), name='quote_success'),
]