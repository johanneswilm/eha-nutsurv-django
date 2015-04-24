# This filter is needed so that django-compressor converts relative font paths in
# scss files to absolute paths, also when no compression takes place.
#
# See https://github.com/django-compressor/django-compressor/issues/226

from compressor.filters.base import CompilerFilter
from compressor.filters.css_default import CssAbsoluteFilter

SASSC_COMMAND = 'sassc -m -I /opt/nutsurv/bower_components/ehealth-bootstrap/ -I bower_components/ehealth-bootstrap/ "{infile}" "{outfile}"'


class SCSSFilter(CompilerFilter):

    def __init__(self, content, attrs, **kwargs):
        super(SCSSFilter, self).__init__(content, command=SASSC_COMMAND, **kwargs)

    def input(self, **kwargs):
        content = super(SCSSFilter, self).input(**kwargs)
        return CssAbsoluteFilter(content).input(**kwargs)
