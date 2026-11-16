from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', kwargs={'slug': self.slug})

class Service(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    icone = models.ImageField(upload_to='service_icons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Actualite(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='actualite_images/', null=True, blank=True)
    video_url = models.URLField('URL de la vidéo (YouTube/Vimeo)', blank=True, null=True)
    video_thumbnail = models.ImageField('Miniature de la vidéo', upload_to='actualite_videos/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Actualité'
        verbose_name_plural = 'Actualités'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('actualite_detail', kwargs={'slug': self.slug})

class ActualiteImage(models.Model):
    actualite = models.ForeignKey(Actualite, on_delete=models.CASCADE, related_name='galerie')
    image = models.ImageField(upload_to='actualite_images/galerie/')
    legende = models.CharField('Légende', max_length=200, blank=True)
    ordre = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        verbose_name = "Image de la galerie"
        verbose_name_plural = "Images de la galerie"
        ordering = ['ordre', 'id']

    def __str__(self):
        return f"{self.actualite.name} - image {self.ordre}"

class Sujet(models.Model):  # ou Suject si vous tenez à la faute
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Sujet'
        verbose_name_plural = 'Sujets'

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    SUJET_CHOICES = [
        ('produits', 'Commande de produits'),
        ('devis', 'Demande de devis'),
        ('support', 'Support technique'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre'),
    ]
    prenom = models.CharField('Prénom', max_length=100)
    nom = models.CharField('Nom', max_length=100)
    email = models.EmailField('Email')
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    entreprise = models.CharField('Entreprise', max_length=200, blank=True)
    sujet = models.CharField('Sujet', max_length=20, choices=SUJET_CHOICES)
    message = models.TextField('Message')
    date_envoi = models.DateTimeField('Date d\'envoi', default=timezone.now)
    lu = models.BooleanField('Lu', default=False)
    repondu = models.BooleanField('Répondu', default=False)
    notes = models.TextField('Notes internes', blank=True)

    class Meta:
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.get_sujet_display()}"

class QuoteRequest(models.Model):
    # Informations client
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    entreprise = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True, help_text="Commentaire supplémentaire")
    notes = models.TextField('Notes internes', blank=True)
    
    # Date et statut
    created_at = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Devis {self.id} - {self.nom} {self.prenom}"

class QuoteItem(models.Model):
    quote = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Produit demandé"
        verbose_name_plural = "Produits demandés"
        constraints = [
            models.UniqueConstraint(fields=['quote', 'product'], name='unique_product_per_quote')
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    