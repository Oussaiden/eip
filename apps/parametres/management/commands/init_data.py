from django.core.management.base import BaseCommand
from apps.parametres.models import (
    TGC, Categorie, Unite, TypeLigneDossier,
    ModePaiement, TypeTransport, TypeMachine, NumerotationDocument, Parametre
)
from apps.clients.models import Client, Contact, AdresseLivraison
from apps.articles.models import Article, Fournisseur


class Command(BaseCommand):
    help = 'Initialise les données de test'

    def handle(self, *args, **kwargs):

        # ── TGC ─────────────────────────────────────────────
        tgc0, _ = TGC.objects.get_or_create(code='TGC0', defaults={
            'libelle': 'TGC 0%', 'taux': 0, 'actif': True, 'date_debut': '2024-01-01'
        })
        tgc11, _ = TGC.objects.get_or_create(code='TGC11', defaults={
            'libelle': 'TGC 11%', 'taux': 11, 'actif': True, 'date_debut': '2024-01-01'
        })
        self.stdout.write('✓ TGC')

        # ── Catégories ───────────────────────────────────────
        cats = ['Papier', 'Encre', 'Consommable', 'Plaques', 'Solvant']
        cat_objs = {}
        for c in cats:
            obj, _ = Categorie.objects.get_or_create(libelle=c, defaults={'actif': True})
            cat_objs[c] = obj
        self.stdout.write('✓ Catégories')

        # ── Unités ───────────────────────────────────────────
        unites = [
            ('Kilogramme', 'kg'),
            ('Gramme', 'g'),
            ('Feuille', 'feuille'),
            ('Litre', 'L'),
            ('Unité', 'u'),
            ('Boîte', 'boîte'),
            ('Rouleau', 'rouleau'),
        ]
        unite_objs = {}
        for libelle, abrev in unites:
            obj, _ = Unite.objects.get_or_create(libelle=libelle, defaults={'abreviation': abrev, 'actif': True})
            unite_objs[libelle] = obj
        self.stdout.write('✓ Unités')

        # ── Types ligne dossier ──────────────────────────────
        types = ['Matière', 'Machine', 'Opérateur', 'Sous-traitance']
        for t in types:
            TypeLigneDossier.objects.get_or_create(libelle=t, defaults={'actif': True})
        self.stdout.write('✓ Types ligne dossier')

        # ── Modes de paiement ────────────────────────────────
        modes = ['Virement bancaire', 'Chèque', 'Espèces', 'Carte bancaire']
        for m in modes:
            ModePaiement.objects.get_or_create(libelle=m, defaults={'actif': True})
        self.stdout.write('✓ Modes de paiement')

        # ── Types de transport ───────────────────────────────
        transports = ['Transporteur externe', 'Camion EIP']
        for t in transports:
            TypeTransport.objects.get_or_create(libelle=t, defaults={'actif': True})
        self.stdout.write('✓ Types de transport')

        # ── Types de machine ─────────────────────────────────
        machines = ['Offset', 'Numérique', 'Finition', 'Grand format']
        for m in machines:
            TypeMachine.objects.get_or_create(libelle=m, defaults={'actif': True})
        self.stdout.write('✓ Types de machine')

        # ── Numérotation ─────────────────────────────────────
        docs = [
            ('devis', 'DEV', '2026', '-', 5),
            ('dossier', 'DOS', '2026', '-', 5),
            ('facture', 'FAC', '2026', '-', 5),
            ('avoir', 'AVO', '2026', '-', 5),
            ('livraison', 'BL', '2026', '-', 5),
            ('commande', 'BC', '2026', '-', 5),
        ]
        for type_doc, prefixe, millesime, sep, longueur in docs:
            NumerotationDocument.objects.get_or_create(type_doc=type_doc, defaults={
                'prefixe': prefixe,
                'millesime': millesime,
                'separateur': sep,
                'longueur': longueur,
                'numero_courant': 1,
                'reset_annuel': True,
            })
        self.stdout.write('✓ Numérotation')

        # ── Paramètres ───────────────────────────────────────
        Parametre.objects.get_or_create(cle='delai_validite_devis', defaults={
            'libelle': 'Délai de validité des devis (jours)',
            'valeur': '30',
            'type': 'entier',
            'categorie': 'general',
            'description': 'Nombre de jours ajoutés à la date du devis pour calculer la date de validité',
        })
        self.stdout.write('✓ Paramètres')

        # ── Fournisseurs ─────────────────────────────────────
        Fournisseur.objects.get_or_create(raison_sociale='Papeterie du Pacifique', defaults={
            'email': 'commandes@papeterie-pacifique.nc',
            'telephone': '27 10 10',
            'adresse': 'Zone Industrielle de Ducos',
            'ville': 'Nouméa',
            'pays': 'Nouvelle-Calédonie',
            'delai_livraison_jours': 3,
            'actif': True,
        })
        Fournisseur.objects.get_or_create(raison_sociale='Encres & Co', defaults={
            'email': 'ventes@encres-co.nc',
            'telephone': '27 20 20',
            'adresse': '15 rue du Commerce',
            'ville': 'Nouméa',
            'pays': 'Nouvelle-Calédonie',
            'delai_livraison_jours': 5,
            'actif': True,
        })
        self.stdout.write('✓ Fournisseurs')

        # ── Articles ─────────────────────────────────────────
        # ref, designation, cat, unite, stock, seuil, pru, pv_ht, tgc_achat, tgc_vente
        articles = [
            ('PAP-001', 'Papier couché 135g A3', 'Papier', 'Feuille', 5000, 500, 15, 25, tgc11, tgc11),
            ('PAP-002', 'Papier offset 80g A4', 'Papier', 'Feuille', 10000, 1000, 5, 9, tgc11, tgc11),
            ('PAP-003', 'Carton 300g A2', 'Papier', 'Feuille', 2000, 200, 25, 42, tgc11, tgc11),
            ('ENC-001', 'Encre noire offset 1kg', 'Encre', 'Kilogramme', 50, 10, 1500, 2500, tgc11, tgc11),
            ('ENC-002', 'Encre cyan offset 1kg', 'Encre', 'Kilogramme', 30, 5, 1700, 2800, tgc11, tgc11),
            ('ENC-003', 'Encre magenta offset 1kg', 'Encre', 'Kilogramme', 30, 5, 1700, 2800, tgc11, tgc11),
            ('ENC-004', 'Encre jaune offset 1kg', 'Encre', 'Kilogramme', 30, 5, 1700, 2800, tgc11, tgc11),
            ('PLA-001', 'Plaque offset A2', 'Plaques', 'Unité', 200, 20, 300, 500, tgc11, tgc11),
            ('CON-001', 'Film plastification mat', 'Consommable', 'Rouleau', 20, 3, 4500, 7500, tgc11, tgc11),
            ('CON-002', 'Film plastification brillant', 'Consommable', 'Rouleau', 20, 3, 4500, 7500, tgc11, tgc11),
        ]
        for ref, des, cat, unite, stock, seuil, pru, pv_ht, tgc_a, tgc_v in articles:
            Article.objects.get_or_create(reference=ref, defaults={
                'designation': des,
                'categorie': cat_objs[cat],
                'unite': unite_objs[unite],
                'stock_actuel': stock,
                'seuil_minimum': seuil,
                'pru_moyen': pru,
                'valeur_stock': stock * pru,
                'prix_vente_ht': pv_ht,
                'tgc_achat': tgc_a,
                'tgc_vente': tgc_v,
                'actif': True,
            })
        self.stdout.write('✓ Articles')

        # ── Clients ──────────────────────────────────────────
        clients_data = [
            ('Mairie de Nouméa', '123456789', 'contact@mairie-noumea.nc', '26 20 00'),
            ('Province Sud', '987654321', 'direction@province-sud.nc', '20 40 00'),
            ('Clinique Kuindo-Magnin', '456789123', 'admin@clinique-km.nc', '26 60 60'),
            ('OPT Nouvelle-Calédonie', '789123456', 'contact@opt.nc', '05 00 00'),
            ('Air Calédonie', '321654987', 'marketing@air-caledonie.nc', '25 21 77'),
            ('Caledonia Invest', '654321987', 'contact@caledonia-invest.nc', '28 30 40'),
            ('CPS Nouvelle-Calédonie', '112233445', 'contact@cps.nc', '25 61 00'),
        ]
        client_objs = {}
        for rs, siret, email, tel in clients_data:
            obj, _ = Client.objects.get_or_create(raison_sociale=rs, defaults={
                'siret': siret,
                'email': email,
                'telephone': tel,
                'actif': True,
            })
            client_objs[rs] = obj
        self.stdout.write('✓ Clients')

        # ── Contacts ─────────────────────────────────────────
        contacts_data = [
            ('Mairie de Nouméa', 'Dupont', 'Jean', 'j.dupont@mairie-noumea.nc', '26 20 01', True, 'Directeur des achats'),
            ('Province Sud', 'Martin', 'Sophie', 's.martin@province-sud.nc', '20 40 01', True, 'Responsable communication'),
            ('Clinique Kuindo-Magnin', 'Bernard', 'Pierre', 'p.bernard@clinique-km.nc', '26 60 61', True, 'Directeur administratif'),
            ('OPT Nouvelle-Calédonie', 'Leblanc', 'Marie', 'm.leblanc@opt.nc', '05 00 01', True, 'Responsable marketing'),
            ('Air Calédonie', 'Petit', 'Paul', 'p.petit@air-caledonie.nc', '25 21 78', True, 'Directeur commercial'),
        ]
        for rs, nom, prenom, email, tel, principal, poste in contacts_data:
            if rs in client_objs:
                Contact.objects.get_or_create(
                    client=client_objs[rs],
                    nom=nom,
                    prenom=prenom,
                    defaults={
                        'email': email,
                        'telephone': tel,
                        'is_principal': principal,
                        'poste': poste,
                    }
                )
        self.stdout.write('✓ Contacts')

        # ── Adresses de livraison ─────────────────────────────
        adresses_data = [
            ('Mairie de Nouméa', 'Siège social', 'BP K5 — 98849 Nouméa Cedex', '', '98800', 'Nouméa', True),
            ('Province Sud', 'Siège social', '1 avenue du Maréchal Foch', '', '98800', 'Nouméa', True),
            ('Clinique Kuindo-Magnin', 'Siège social', '7 rue Paul Doumer', '', '98800', 'Nouméa', True),
            ('OPT Nouvelle-Calédonie', 'Siège social', '12 rue Faidherbe', '', '98800', 'Nouméa', True),
            ('Air Calédonie', 'Aéroport Magenta', 'Aéroport de Magenta', '', '98800', 'Nouméa', True),
        ]
        for rs, libelle, adresse, complement, cp, ville, default in adresses_data:
            if rs in client_objs:
                AdresseLivraison.objects.get_or_create(
                    client=client_objs[rs],
                    libelle=libelle,
                    defaults={
                        'adresse': adresse,
                        'complement': complement,
                        'code_postal': cp,
                        'ville': ville,
                        'pays': 'Nouvelle-Calédonie',
                        'is_default': default,
                    }
                )
        self.stdout.write('✓ Adresses de livraison')

        self.stdout.write(self.style.SUCCESS('\n✅ Données de test initialisées avec succès !'))