from django.db import models


class PageVisits(models.Model):
    path = models.TextField(blank=True,null=True)
    timestamp = models.TimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Page Visits"
        verbose_name = "Page Visit"

    def __str__(self) -> str:
        return self.path

