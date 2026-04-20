from django.db import models


class Lead(models.Model):

    STATUS_CHOICES = [
        ("NEW", "New"),
        ("ENRICHING", "Enriching"),
        ("ENRICHED", "Enriched"),
        ("EMAIL_SENT", "Email Sent"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(max_length=100)
    company = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    company_summary = models.TextField(null=True, blank=True)
    generated_email = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.company}"
