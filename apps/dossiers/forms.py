from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Devis, VarianteDevis, LigneDevis, Dossier
from apps.articles.models import Article
from apps.parametres.models import TGC


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'date', 'date_validite', 'description', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_validite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                'placeholder': 'Format, support, couleurs, finition...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                'placeholder': 'Notes internes...'}),
        }


class VarianteDevisForm(forms.ModelForm):
    class Meta:
        model = VarianteDevis
        fields = ['libelle', 'remise_globale']
        widgets = {
            'libelle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 500 ex, 1000 ex, Option A...'
            }),
            'remise_globale': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
        }
        labels = {
            'remise_globale': 'Remise globale (%)',
        }


class LigneDevisForm(forms.ModelForm):

    tgc_obj = forms.ModelChoiceField(
        queryset=TGC.objects.filter(actif=True).order_by('taux'),
        required=False,
        empty_label='TGC 0%',
        label='TGC',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tgc'}),
    )

    class Meta:
        model = LigneDevis
        fields = ['type', 'article', 'designation', 'qte', 'pu', 'pru', 'remise']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select', 'id': 'id_type'}),
            'article': forms.Select(attrs={'class': 'form-select', 'id': 'id_article'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_designation'}),
            'qte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_qte'}),
            'pu': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_pu'}),
            'pru': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_pru'}),
            'remise': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'id': 'id_remise'}),
        }
        labels = {
            'pru': 'PRU',
            'remise': 'Remise (%)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['article'].queryset = Article.objects.filter(actif=True).order_by('designation')
        self.fields['article'].empty_label = '— Aucun article —'
        self.fields['article'].required = False
        self.fields['designation'].required = False

        # Pré-remplir tgc_obj depuis taux_tgc de la ligne existante
        if self.instance and self.instance.pk and self.instance.taux_tgc:
            try:
                tgc = TGC.objects.get(taux=self.instance.taux_tgc, actif=True)
                self.fields['tgc_obj'].initial = tgc
            except TGC.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        type_ligne = cleaned_data.get('type')
        article = cleaned_data.get('article')
        designation = cleaned_data.get('designation')

        if type_ligne == 'libre' and not article and not designation:
            self.add_error('designation', 'La désignation est obligatoire pour une ligne libre sans article.')

        # Convertir l'objet TGC en taux décimal
        tgc_obj = cleaned_data.get('tgc_obj')
        if tgc_obj:
            cleaned_data['taux_tgc'] = tgc_obj.taux
        else:
            cleaned_data['taux_tgc'] = 0

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.taux_tgc = self.cleaned_data.get('taux_tgc', 0)
        if instance.article and not instance.designation:
            instance.designation = instance.article.designation
        if commit:
            instance.save()
        return instance


class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = ['date_livraison', 'priorite', 'visible_client', 'notes', 'notes_fab']
        widgets = {
            'date_livraison': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'visible_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes_fab': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }