from django.contrib import admin

from models import JSONDocument, JSONDocumentType
from models import Alert


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')

admin.site.register((JSONDocument, JSONDocumentType))
admin.site.register(Alert, AlertAdmin)
