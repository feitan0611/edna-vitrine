from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ContactMessage, QuoteRequest

# Formulaire d'inscription
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Mot de passe', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmation mot de passe', 'class': 'form-control'})
        # Optionnel : personnaliser les labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse e-mail"
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


# Formulaire de contact (lié au modèle ContactMessage)
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['prenom', 'nom', 'email', 'telephone', 'entreprise', 'sujet', 'message']
        widgets = {
            'prenom': forms.TextInput(attrs={
                'placeholder': 'Votre prénom',
                'class': 'form-control',
                'required': True
            }),
            'nom': forms.TextInput(attrs={
                'placeholder': 'Votre nom',
                'class': 'form-control',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'votre@email.com',
                'class': 'form-control',
                'required': True
            }),
            'telephone': forms.TextInput(attrs={
                'placeholder': '+225 00 00 00 00',
                'class': 'form-control'
            }),
            'entreprise': forms.TextInput(attrs={
                'placeholder': 'Nom de votre entreprise',
                'class': 'form-control'
            }),
            'sujet': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Décrivez votre demande...',
                'class': 'form-control',
                'rows': 5,
                'required': True
            }),
        }
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'email': 'Email',
            'telephone': 'Téléphone',
            'entreprise': 'Entreprise',
            'sujet': 'Sujet',
            'message': 'Message',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs non requis si souhaité
        self.fields['telephone'].required = False
        self.fields['entreprise'].required = False
        # Définir les choix du champ sujet dynamiquement (si ce n'est pas déjà fait dans le modèle)
        self.fields['sujet'].choices = ContactMessage.SUJET_CHOICES

class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ['nom', 'prenom', 'email', 'telephone', 'entreprise', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'placeholder': 'Entreprise (optionnel)', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Votre message (optionnel)', 'class': 'form-control', 'rows': 4}),
        }