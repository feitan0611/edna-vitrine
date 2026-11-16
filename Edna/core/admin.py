from django.contrib import admin
from .models import Service, Actualite, ActualiteImage, ContactMessage, Sujet, Categorie, Product
from .models import QuoteRequest, QuoteItem
from django.conf import settings
from django.core.mail import send_mail

# ========== SERVICES ==========
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}

# ========== ACTUALITÉS ==========
class ActualiteImageInline(admin.TabularInline):
    model = ActualiteImage
    extra = 1
    fields = ('image', 'legende', 'ordre')

@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'is_featured', 'created_at', 'updated_at', 'has_video')
    list_filter = ('is_published', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)   # <--- AJOUT
    inlines = [ActualiteImageInline]
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Média', {
            'fields': ('image', 'video_url', 'video_thumbnail')
        }),
        ('Publication', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Générer la miniature automatiquement si une URL vidéo est présente
        if obj.video_url and not obj.video_thumbnail:
            import re
            match = re.search(r'(?:youtu\.be/|youtube\.com/watch\?v=)([^&]+)', obj.video_url)
            if match:
                vid_id = match.group(1)
                obj.video_thumbnail = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
        super().save_model(request, obj, form, change)

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = "Vidéo"

# ========== SUJET ==========
@admin.register(Sujet)
class SujetAdmin(admin.ModelAdmin):
    list_display = ('name',)

# ========== CATÉGORIE & PRODUIT ==========
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'price', 'is_available')

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'categorie', 'price', 'created_at', 'updated_at')
    list_filter = ('categorie', 'is_available')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# ========== MESSAGES DE CONTACT ==========
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'sujet', 'date_envoi', 'lu', 'repondu']
    list_filter = ['sujet', 'lu', 'repondu']
    search_fields = ['nom', 'prenom', 'email']
    readonly_fields = ['date_envoi']
    fieldsets = (
        ('Informations client', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'entreprise')
        }),
        ('Message', {
            'fields': ('sujet', 'message', 'date_envoi')
        }),
        ('Traitement', {
            'fields': ('lu', 'repondu', 'notes')
        }),
    )

    def save_model(self, request, obj, form, change):
        original = None
        if change:
            original = self.model.objects.get(pk=obj.pk)
        if change and original.notes != obj.notes and obj.notes.strip():
            subject = f"Réponse à votre message - EDNA&SA"
            message = f"""
Bonjour {obj.prenom} {obj.nom},

Nous avons bien reçu votre message du {obj.date_envoi.strftime('%d/%m/%Y')} concernant {obj.get_sujet_display()}.

Réponse de notre équipe :
{obj.notes}

Pour toute question supplémentaire, n'hésitez pas à nous contacter.

Cordialement,
L'équipe EDNA&SA
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [obj.email],
                fail_silently=False,
            )
        super().save_model(request, obj, form, change)

# ========== DEMANDES DE DEVIS ==========
class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    readonly_fields = ['product', 'quantity']

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'prenom', 'email', 'created_at', 'traite']
    list_filter = ['traite']
    inlines = [QuoteItemInline]
    fieldsets = (
        ('Informations client', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'entreprise')
        }),
        ('Demande', {
            'fields': ('message', 'created_at')
        }),
        ('Traitement', {
            'fields': ('traite', 'notes')
        }),
    )
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        original = None
        if change:
            original = self.model.objects.get(pk=obj.pk)
        if change and original.notes != obj.notes and obj.notes.strip():
            subject = f"Réponse à votre demande de devis - EDNA&SA"
            items = obj.items.all()
            produits = "\n".join([f"- {item.product.name} x{item.quantity} : {item.product.price * item.quantity} FCFA" for item in items])
            total = sum(item.product.price * item.quantity for item in items)
            message = f"""
Bonjour {obj.prenom} {obj.nom},

Merci pour votre demande de devis du {obj.created_at.strftime('%d/%m/%Y')}.

Détail de votre demande :
{produits}
Total : {total} FCFA

Réponse de notre équipe :
{obj.notes}

N'hésitez pas à nous contacter pour tout complément d'information.

Cordialement,
L'équipe EDNA&SA
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [obj.email],
                fail_silently=False,
            )
        super().save_model(request, obj, form, change)