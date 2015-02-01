from django.db import models

from jsonfield import JSONField

class FormhubData(models.Model):
    contents = JSONField(null=True, blank=True, help_text=' ')
    uuid = models.CharField(max_length=256,unique=True)

    def __unicode__(self):
        return self.uuid

    class Meta:
        verbose_name_plural = 'Formhub Data Entries'
