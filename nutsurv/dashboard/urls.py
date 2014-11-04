__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


from django.conf.urls import include, patterns

from tastypie.api import Api
from api.resources import JSONDocumentResource

v1_api = Api(api_name='v1')
v1_api.register(JSONDocumentResource())

urlpatterns = patterns('',
                       (r'^api/', include(v1_api.urls)),
                       )

