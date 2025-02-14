from django.db import models
from django.utils import timezone


class ContextElement(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    important = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.key}: {self.value}"


class Item(models.Model):
    value = models.CharField(max_length=255)
    context = models.ManyToManyField(ContextElement, blank=True)
    score = models.FloatField(default=0, null=True, blank=True)
    approved = models.BooleanField(default=False)
    suggested_by_reviewer = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Correction(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Invalid'),
    ]

    subject = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='subject_corrections')
    hypotheses = models.ManyToManyField(Item, related_name='hypothesis_corrections')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    scope_id = models.IntegerField(default=0)

    def __str__(self):
        return f"Correction for {self.subject.value} (Status: {self.get_status_display()})"
