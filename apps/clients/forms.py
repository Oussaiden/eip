from django import forms
from .models import Client, Contact, AdresseLivraison


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['raison_sociale', 'siret', 'email', 'telephone', 'notes', 'actif']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raison sociale'}),
            'siret': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RIDET'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'siret': 'RIDET',
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'telephone', 'telephone_mobile', 'poste', 'is_principal']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'is_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AdresseLivraisonForm(forms.ModelForm):
    class Meta:
        model = AdresseLivraison
        fields = ['libelle', 'adresse', 'complement', 'code_postal', 'ville', 'pays', 'is_default']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }