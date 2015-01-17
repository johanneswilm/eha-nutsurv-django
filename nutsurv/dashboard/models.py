from django.db import models
from django.core.validators import MinValueValidator

import django.contrib.gis.db.models as gismodels
from django.contrib.gis.geos import Point

from jsonfield import JSONField
from jsonschema import validate, ValidationError

from fields import MaxOneActiveQuestionnaireField


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
        return u'JSON Data for Clusters (pk: {}; created: {}; last modified: ' \
               u'{})'.format(self.pk, self.created, self.last_modified)

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
        # The cluster JSON data provided stores cluster_ids as strings and some
        # other parts of the system use integers for that.
        cluster_id = str(cluster_id)
        if 'clusters' in self.json:
            if cluster_id in self.json['clusters']:
                cluster = self.json['clusters'][cluster_id]
        return cluster


class Area(gismodels.Model):
    """Written for a geospatial data set containing the following fields:
    name_0 - country (top level)
    name_1 - state (middle level, contained in area name_0)
    name_2 - LGA (subarea of name_1)
    varname_2 - an alternative name for area name_2 (optional, can be empty)
    """
    # Attributes of interest from the shapefile.
    name_0 = gismodels.CharField(
        max_length=255,
        help_text='The area two levels higher than this one (i.e. the area '
                  'containing the area which contains this area (e.g. the name '
                  'of a country))'
    )
    name_1 = gismodels.CharField(
        max_length=255,
        help_text='The area one level higher than this one (i.e. the area '
                  'containing this area (e.g. the name of a state))'
    )
    name_2 = gismodels.CharField(
        max_length=255,
        help_text='The name of this area (e.g. the name of an LGA))'
    )
    varname_2 = gismodels.CharField(
        max_length=255, blank=True,
        help_text='Alternative name for this area (optional, can be left blank)'
    )
    # A GeoDjango-specific geometry field.
    mpoly = gismodels.MultiPolygonField(
        help_text='A multi-polygon field defining boundaries of this area'
    )
    # Override the model's default manager to enable spatial queries.
    objects = gismodels.GeoManager()

    def contains_location(self, location):
        """Returns True if location (longitude, latitude) lies within this area.
        Otherwise, it returns False.  Assumes that the location argument uses
        the same srid as the area.
        """
        longitude = float(location[0])
        latitude = float(location[1])
        point = Point(longitude, latitude, srid=self.mpoly.srid)
        output = self.mpoly.contains(point)
        return output

    def __unicode__(self):
        if self.varname_2:
            aka = u' (a.k.a. {})'.format(self.varname_2)
        else:
            aka = u''
        return u'{}/{}/{}{}'.format(self.name_0, self.name_1, self.name_2, aka)


class LGA(Area):
    def get_lga_name(self):
        return self.name_2

    def get_lga_alternative_name(self):
        return self.varname_2

    def get_lga_names(self):
        return [self.get_lga_name(), self.get_lga_alternative_name()]

    def get_state_name(self):
        return self.name_1

    def get_country_name(self):
        return self.name_0

    @classmethod
    def find_lga(cls, name, state_name, country_name=None):
        if country_name:
            query = {'name_0': country_name, 'name_1': state_name}
        else:
            query = {'name_1': state_name}
        found = 0
        query_result = []
        for lga_name_field in ('name_2', 'varname_2'):
            query[lga_name_field] = name
            query_result = cls.objects.filter(**query)
            found = query_result.count()
            if found == 0:
                del query[lga_name_field]
            else:
                break
        if found == 0:
            return None
        elif found == 1:
            return query_result[0]
        else:
            if country_name:
                country_part = u' and country "{}"'.format(country_name)
            else:
                country_part = u''
            raise RuntimeError(u'More than one LGA named "{}" in state "{}"{} '
                               u'found!'.format(name, state_name, country_part))


class QuestionnaireSpecification(models.Model):
    name_or_id = models.CharField(
        max_length=255, unique=True, blank=False,
        help_text=u'Please enter a unique name or id of your new questionnaire '
                  u'specification.')
    specification = models.TextField(
        blank=False,
        help_text=u'Please enter or copy & paste your new questionnaire '
                  u'specification written in the QSL (Questionnaire '
                  u'Specification Language). <br />'
                  u'Please pay particular attention to indentation as '
                  u'indentation levels are part of the QSL and incorrect '
                  u'indentation will most likely produce nonsensical '
                  u'specification.<br />'
                  u'To familiarise yourself with the version of QSL used here '
                  u'please read <a href="/static/qsl.html" target="_blank">'
                  u'this document</a>.')
    active = MaxOneActiveQuestionnaireField(
        default=False,
        help_text=u'Activate this questionnaire specification.  Only one '
                  u'questionnaire specification may be active at any given '
                  u'time.')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name_or_id

    @classmethod
    def get_active(cls):
        active_qss = cls.objects.filter(active__exact=True)
        c = active_qss.count()
        if c == 1:
            return active_qss[0]
        elif c == 0:
            return None
        else:
            raise RuntimeError(u'More than one active questionnaire '
                               u'specification found.  This should not happen. '
                               u'Please check the database.')

    @classmethod
    def get_most_recently_created(cls):
        questionnaire_specifications = cls.objects.order_by('-created')
        if questionnaire_specifications:
            return questionnaire_specifications[0]
        else:
            return None

    @classmethod
    def get_most_recently_modified(cls):
        questionnaire_specifications = cls.objects.order_by('-last_modified')
        if questionnaire_specifications:
            return questionnaire_specifications[0]
        else:
            return None
