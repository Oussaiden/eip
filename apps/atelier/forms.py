from django import forms
from apps.parametres.models import TypeMachine
from apps.planning.models import Machine


class MachineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].queryset = TypeMachine.objects.filter(actif=True).order_by('libelle')
        self.fields['type'].empty_label = 'Sélectionner un type'

    class Meta:
        model = Machine
        fields = [
            'reference', 'nom', 'type', 'description',
            'format_min_largeur', 'format_min_hauteur',
            'format_max_largeur', 'format_max_hauteur',
            'nb_couleurs', 'vitesse_max', 'recto_verso', 'vitesse_recto_verso',
            'temps_mise_en_oeuvre', 'temps_calage', 'temps_nettoyage',
            'cout_nrj_heure', 'cout_amortissement_heure', 'cout_entretien_heure',
            'taux_gache', 'actif',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'format_min_largeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'ex: 100'}),
            'format_min_hauteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'ex: 150'}),
            'format_max_largeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'ex: 720'}),
            'format_max_hauteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'ex: 1020'}),
            'nb_couleurs': forms.NumberInput(attrs={'class': 'form-control'}),
            'vitesse_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'recto_verso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vitesse_recto_verso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temps_mise_en_oeuvre': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temps_calage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temps_nettoyage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'cout_nrj_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cout_amortissement_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cout_entretien_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taux_gache': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
