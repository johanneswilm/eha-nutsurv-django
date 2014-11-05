from django.contrib import admin

from models import JSONDocument, JSONDocumentType


admin.site.register((JSONDocument, JSONDocumentType))
