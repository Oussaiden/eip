from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLES = [
        ('direction', 'Direction'),
        ('technico_commercial', 'Technico-Commercial'),
        ('chef_fab', 'Chef de FAB'),
        ('atelier', 'Atelier'),
        ('comptable', 'Comptable'),
        ('stock', 'Stock'),
        ('accueil', 'Accueil'),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLES,
        blank=False,
        null=False,
    )

    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_direction(self):
        return self.role == 'direction'

    @property
    def is_technico_commercial(self):
        return self.role == 'technico_commercial'

    @property
    def is_chef_fab(self):
        return self.role == 'chef_fab'

    @property
    def is_atelier(self):
        return self.role == 'atelier'

    @property
    def is_comptable(self):
        return self.role == 'comptable'

    @property
    def is_stock(self):
        return self.role == 'stock'

    @property
    def is_accueil(self):
        return self.role == 'accueil'