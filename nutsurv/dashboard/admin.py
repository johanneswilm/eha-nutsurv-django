from django.contrib import admin

from models import JSONDocument, JSONDocumentType
from models import Alert
from models import ClustersJSON


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')

admin.site.register((JSONDocument, JSONDocumentType, ClustersJSON))
admin.site.register(Alert, AlertAdmin)
