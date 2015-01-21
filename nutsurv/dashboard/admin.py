from django.contrib import admin

from models import JSONDocument, JSONDocumentType
from models import Alert
from models import ClustersJSON
from models import LGA
from models import QuestionnaireSpecification
from models import ClustersPerState
from models import States
from models import StatesWithReserveClusters
from models import ClustersPerTeam


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class QuestionnaireSpecificationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersJSONAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersPerStateAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class StatesAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class StatesWithReserveClustersAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersPerTeamAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


admin.site.register(Alert, AlertAdmin)
admin.site.register(ClustersJSON, ClustersJSONAdmin)
admin.site.register(QuestionnaireSpecification, QuestionnaireSpecificationAdmin)
admin.site.register(ClustersPerState, ClustersPerStateAdmin)
admin.site.register(States, StatesAdmin)
admin.site.register(StatesWithReserveClusters, StatesWithReserveClustersAdmin)
admin.site.register(ClustersPerTeam, ClustersPerTeamAdmin)


admin.site.register(
    (
        JSONDocument,
        JSONDocumentType,
        LGA,
    )
)
