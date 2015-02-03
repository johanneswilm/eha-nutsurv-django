__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.exceptions import ImmediateHttpResponse

from dashboard.models import HouseholdSurveyJSON


class HouseholdSurveyValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'The input is empty.'}
        if not isinstance(bundle.data, dict):
            return {'__all__': 'The input is not a valid dictionary.'}
        if 'json' not in bundle.data:
            return {'__all__': 'No top-level "json" object detected.'}
        if 'uuid' not in bundle.data:
            return {'__all__': 'No "uuid" object in "json" detected.'}
        # For possible future use.
        errors = {}
        return errors


class HouseholdSurveyJSONResource(ModelResource):
    class Meta:
        queryset = HouseholdSurveyJSON.objects.all()
        allowed_methods = ['post']
        fields = ['json', 'uuid']
        authorization = Authorization()
        validation = HouseholdSurveyValidation()
        resource_name = 'jsondocument'

    def obj_create(self, bundle, **kwargs):
        try:
            uuid = bundle.data['json']['uuid']
        except KeyError:
            bundle.errors['uuid'] = 'No /json/uuid.'
            raise ImmediateHttpResponse(
                response=self.error_response(bundle.request, bundle.errors)
            )

        # Get rid of objects with the same uuid (in case they exist).
        HouseholdSurveyJSON.objects.filter(uuid=uuid).delete()

        # Set the uuid field to the value detected in the JSON document.
        bundle.data['uuid'] = uuid

        # Create a new object based on bundle.
        bundle = super(HouseholdSurveyJSONResource,
                       self).obj_create(bundle, **kwargs)

        return bundle
