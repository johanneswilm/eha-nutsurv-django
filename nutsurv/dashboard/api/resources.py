__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from dashboard.models import JSONDocument


class JSONDocumentResource(ModelResource):
    class Meta:
        queryset = JSONDocument.objects.all()
        allowed_methods = ['post']
        fields = ['json']
        authorization = Authorization()
