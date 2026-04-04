import uuid
from django.db import models


class Notification(models.Model):
    TYPES = [
        ('stock_bas', 'Stock bas'),
        ('stock_insuffisant', 'Stock insuffisant'),
        ('derive_rentabilite', 'Dérive rentabilité'),
        ('validation_requise', 'Validation requise'),
        ('statut_dossier', 'Changement statut dossier'),
        ('autre', 'Autre'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=TYPES)
    titre = models.CharField(max_length=255)
    message = models.TextField()
    objet_id = models.UUIDField(null=True, blank=True)
    objet_type = models.CharField(max_length=50, blank=True)
    lue = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} — {self.user.get_full_name()} — {self.titre}"
