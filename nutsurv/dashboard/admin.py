from django.contrib import admin

from models import JSONDocument, JSONDocumentType
from models import Alert
from models import ClustersJSON
from models import LGA
from models import QuestionnaireSpecification


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class QuestionnaireSpecificationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersJSONAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


admin.site.register(Alert, AlertAdmin)
admin.site.register(ClustersJSON, ClustersJSONAdmin)
admin.site.register(QuestionnaireSpecification, QuestionnaireSpecificationAdmin)


admin.site.register(
    (
        JSONDocument,
        JSONDocumentType,
        LGA,
    )
)

