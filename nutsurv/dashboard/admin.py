from django.contrib import admin

from models import HouseholdSurveyJSON
from models import Alert
from models import Clusters
from models import SecondAdminLevel
from models import QuestionnaireSpecification
from models import ClustersPerFirstAdminLevel
from models import FirstAdminLevels
from models import FirstAdminLevelsReserveClusters


class AlertAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class QuestionnaireSpecificationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class ClustersPerFirstAdminLevelAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class FirstAdminLevelsAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


class FirstAdminLevelsReserveClustersAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_modified')


admin.site.register(Alert, AlertAdmin)
admin.site.register(Clusters, ClustersAdmin)
admin.site.register(QuestionnaireSpecification, QuestionnaireSpecificationAdmin)
admin.site.register(ClustersPerFirstAdminLevel, ClustersPerFirstAdminLevelAdmin)
admin.site.register(FirstAdminLevels, FirstAdminLevelsAdmin)
admin.site.register(FirstAdminLevelsReserveClusters, FirstAdminLevelsReserveClustersAdmin)


admin.site.register(
    (
        HouseholdSurveyJSON,
        SecondAdminLevel,
    )
)
