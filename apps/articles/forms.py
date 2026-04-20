from django import forms
from .models import ArticleStock, ArticleService, Fournisseur, ArticleFournisseur, MouvementStock
from apps.parametres.models import Categorie, Unite, TGC, Section


class ArticleStockForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].queryset = Categorie.objects.filter(actif=True).order_by('libelle')
        self.fields['categorie'].empty_label = 'Sélectionner une catégorie'
        self.fields['unite'].queryset = Unite.objects.filter(actif=True).order_by('libelle')
        self.fields['unite'].empty_label = 'Sélectionner une unité'
        self.fields['tgc_achat'].queryset = TGC.objects.filter(actif=True).order_by('taux')
        self.fields['tgc_achat'].empty_label = 'TGC 0%'
        self.fields['tgc_vente'].queryset = TGC.objects.filter(actif=True).order_by('taux')
        self.fields['tgc_vente'].empty_label = 'TGC 0%'
        self.fields['sections'].queryset = Section.objects.filter(actif=True).order_by('ordre', 'libelle')

    class Meta:
        model = ArticleStock
        fields = [
            'reference', 'designation', 'categorie', 'unite',
            'sections', 'tgc_achat', 'tgc_vente',
            'prix_vente_ht', 'seuil_minimum',
            'notes', 'actif'
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'tgc_achat': forms.Select(attrs={'class': 'form-select'}),
            'tgc_vente': forms.Select(attrs={'class': 'form-select'}),
            'prix_vente_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'seuil_minimum': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sections': forms.CheckboxSelectMultiple(),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sections': 'Sections',
            'prix_vente_ht': 'Prix de vente HT',
            'tgc_achat': 'TGC achat',
            'tgc_vente': 'TGC vente',
            'seuil_minimum': 'Seuil minimum stock',
        }


class ArticleServiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].queryset = Categorie.objects.filter(actif=True).order_by('libelle')
        self.fields['categorie'].empty_label = 'Sélectionner une catégorie'
        self.fields['unite'].queryset = Unite.objects.filter(actif=True).order_by('libelle')
        self.fields['unite'].empty_label = 'Sélectionner une unité'
        self.fields['tgc_vente'].queryset = TGC.objects.filter(actif=True).order_by('taux')
        self.fields['tgc_vente'].empty_label = 'TGC 0%'
        self.fields['sections'].queryset = Section.objects.filter(actif=True).order_by('ordre', 'libelle')

    class Meta:
        model = ArticleService
        fields = [
            'reference', 'designation', 'categorie', 'unite',
            'sections', 'tgc_vente', 'prix_revient', 'prix_vente_ht',
            'notes', 'actif'
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'tgc_vente': forms.Select(attrs={'class': 'form-select'}),
            'prix_revient': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sections': forms.CheckboxSelectMultiple(),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sections': 'Sections',
            'prix_revient': 'Prix de revient',
            'prix_vente_ht': 'Prix de vente HT',
            'tgc_vente': 'TGC vente',
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['raison_sociale', 'email', 'telephone', 'adresse', 'ville', 'pays', 'delai_livraison_jours', 'notes', 'actif']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'delai_livraison_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ArticleFournisseurForm(forms.ModelForm):
    class Meta:
        model = ArticleFournisseur
        fields = ['fournisseur', 'reference_fournisseur', 'prix_unitaire', 'is_prefere']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'reference_fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_prefere': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['type', 'quantite', 'prix_achat', 'motif']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                'placeholder': 'Prix achat unitaire (entrée uniquement)'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
        }
