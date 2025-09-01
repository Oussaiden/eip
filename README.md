# EPI
## But:
EPI est une application web. Permettant la gestion d'une imprimerie.
## Articulation du projet :
1. App login (auth)  
[x] Connexion / déconnexion  
[] Gestion utilisateurs (création, permissions)  
[] Middleware de sécurité
2. App accueil  
[] Accès après login  
[] Dashboard  
[] Menu
3. App stock  
[] Accès après login  
[] Entrées des articles  
[] Sorties automatiques  
[] Ajustements manuel du stock  
[] Visualisation des mouvements  
[] Alertes ou indicateurs clés
4. App devis  
[] Accès après login   
[] Liste des devis  
[] Création devis  
[] Modification devis  
[] Suppression devis (case à cocher)  
[] Impression devis   
[] Duplication devis  
[] Transformation devis vers dossier/tâche/facture  
[] Alertes ou indicateurs clés 
5. App dossier  
[] Accès après login   
[] Liste des dossiers  
[] Création dossiers  
[] Modification dossiers  
[] Suppression dossiers (case à cocher)  
[] Impression dossiers   
[] Duplication dossiers  
[] Transformation dossiers vers facture/devis/tâches  
[] Alertes ou indicateurs clés
6. App facture  
[] Accès après login   
[] Liste des factures  
[] Création facture  
[] Modification facture  
[] Suppression facture (case à cocher)  
[] Impression facture   
[] Duplication facture  
[] Transformation facture vers dossier/devis/tâche  
[] Alertes ou indicateurs clés
7. App tâche 
[] Accès après login   
[] Liste des tâches  
[] Création tâche  
[] Modification tâche  
[] Suppression tâche (case à cocher)  
[] Impression tâche   
[] Duplication tâche  
[] Alertes ou indicateurs clés 
8. App livraison  
[] Accès après login   
[] Liste des livraisons  
[] Création livraison  
[] Modification livraison  
[] Suppression livraison (case à cocher)  
[] Impression livraison   
[] Duplication livraison  
[] Alertes ou indicateurs clés  
9. App client 
[] Accès après login   
[] Liste des clients  
[] Création client  
[] Modification client  
[] Suppression client (case à cocher)  
[] Impression fiche client   
[] Duplication client  
[] Alertes ou indicateurs clés  
10. App article
[] Accès après login   
[] Liste des articles  
[] Création article  
[] Modification article  
[] Suppression article (case à cocher)  
[] Impression fiche article   
[] Duplication article  
[] Alertes ou indicateurs clés  
11. App pilotage
[] Accès après login   
[] Budget  
[] Recettes  
[] Dépenses   
[] KPI coût, delais, productivité, risque  
[] Alertes ou indicateurs clés
## Structure
Python  
Django  
Postgres  
Docker  
Hébergement?
