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
                if already_true[0].pk != model_instance.pk \
                        or already_true.count() > 1:
                    raise exceptions.ValidationError(
                        u'Another active questionnaire specification found.  '
                        u'There can be only one.  Please deactivate the '
                        u'currently active questionnaire specification before '
                        u'activating this one.')
        super(MaxOneActiveQuestionnaireField, self).validate(
            value, model_instance)


class UniqueActiveField(BooleanField):

    """This boolean field can be checked for maximum one instance of a model
    class at a time.
    It is useful if you need to define a model with a boolean field which may
    be set to true only for one object per class (so there may potentially
    exist many objects of that class but only one of them can be checked using
    this field).
    """

    def validate(self, value, model_instance):
        """Validates value and throws ValidationError in case there is another
        instance of a model with its UniqueActiveField set to true.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value:
            query = {'{}__exact'.format(self.name): True, }
            already_active = model_instance._default_manager.filter(**query)
            if already_active:
                if already_active[0].pk != model_instance.pk\
                        or already_active.count() > 1:
                    model_name = model_instance._meta.verbose_name
                    raise exceptions.ValidationError(
                        u'Another active "{}" found.  There can be only one.  '
                        u'Please deactivate the currently active "{}" before '
                        u'activating this one.'.format(model_name, model_name)
                    )
        super(UniqueActiveField, self).validate(value, model_instance)
