from django.db import models
from django.core.validators import MinValueValidator

from jsonfield import JSONField
from jsonschema import validate, ValidationError


class JSONDocument(models.Model):
    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')

    def guess_type(self, list_of_json_document_types):
        """Matches the stored JSON document with the document types provided
        using list_of_json_document_types.  The order of the JSONDocumentType
        objects determines their priority as the method stops as soon as the
        first match is found.

        :param list_of_json_document_types:
        :return: the matched JSONDocumentType or None if no match found
        """
        for json_document_type in list_of_json_document_types:
            if json_document_type.matches(self):
                return json_document_type
        return None


class JSONDocumentType(models.Model):
    name = models.CharField(max_length=255)
    schema = JSONField(null=True, blank=True, help_text=' ')
    priority = models.IntegerField(unique=True, blank=True, null=True,
                                   default=10,
                                   validators=[MinValueValidator(0)],
                                   help_text='Leave empty for the lowest '
                                             'priority'
                                   )

    def matches(self, json_document):
        try:
            validate(json_document.json, self.schema)
        except ValidationError:
            matches = False
        else:
            matches = True
        return matches

    @staticmethod
    def get_all_by_priority():
        return JSONDocumentType.objects.all().order_by('priority')

    def __unicode__(self):
        return self.name


class Alert(models.Model):
    text = models.TextField()
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if self.archived:
            archived = u', archived'
        else:
            archived = u''
        return u'{} (alert #{}{})'.format(self.text, self.pk, archived)


class ClustersJSON(models.Model):
    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'pk: {}; created: {}; last modified: {})'.format(
            self.pk, self.created, self.last_modified)

    @classmethod
    def get_most_recently_created(cls):
        clusters = cls.objects.order_by('-created')
        if clusters:
            return clusters[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls):
        clusters = cls.objects.order_by('-last_modified')
        if clusters:
            return clusters[0]
        else:
            return None

    @classmethod
    def get_cluster_from_most_recently_modified(cls, cluster_id):
        clusters = cls.get_most_recently_modified()
        if clusters:
            return clusters.get_cluster(cluster_id)
        else:
            return None

    @classmethod
    def get_cluster_from_most_recently_created(cls, cluster_id):
        clusters = cls.get_most_recently_created()
        if clusters:
            return clusters.get_cluster(cluster_id)
        else:
            return None

    def get_cluster(self, cluster_id):
        cluster = None
        if 'clusters' in self.json:
            if str(cluster_id) in self.json['clusters']:
                cluster = self.json['clusters'][cluster_id]
        return cluster
