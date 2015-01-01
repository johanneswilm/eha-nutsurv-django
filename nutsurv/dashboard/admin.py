from django.contrib import admin

from models import JSONDocument, JSONDocumentType
from models import Alert
from models import ClustersJSON
from models import LGA


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')

admin.site.register((JSONDocument, JSONDocumentType, ClustersJSON, LGA))
admin.site.register(Alert, AlertAdmin)
