from django.db.models.fields import BooleanField
from django.core import exceptions


class MaxOneActiveQuestionnaireField(BooleanField):
    def validate(self, value, model_instance):
        """Validates value and throws ValidationError.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value:
            kwas = {'{}__exact'.format(self.name): True}
            already_true = model_instance._default_manager.filter(**kwas)
            if already_true:
                if already_true[0].pk != model_instance.pk\
                        or already_true.count() > 1:
                    raise exceptions.ValidationError(
                        u'Another active questionnaire specification found.  '
                        u'There can be only one.  Please deactivate the '
                        u'currently active questionnaire specification before '
                        u'activating this one.')
        super(MaxOneActiveQuestionnaireField, self).validate(
            value, model_instance)
