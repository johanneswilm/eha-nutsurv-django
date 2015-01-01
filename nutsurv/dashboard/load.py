from django.contrib.gis.utils import LayerMapping
from models import LGA

# An exemplary mapping for data downloaded from 'http://www.diva-gis.org/gdata'.
# To use it, download 'Administrative areas' for 'Nigeria' from the web page
# mentioned above.  Unzip the archive and use function import_data_from_file()
# with the filepath argument pointing to file NGA_adm2.shp from the archive.
lga_mapping = {
    'name_0': 'NAME_0',
    'name_1': 'NAME_1',
    'name_2': 'NAME_2',
    'varname_2': 'VARNAME_2',
    'mpoly': 'MULTIPOLYGON',
}


def import_data_from_file(filepath, mapping=lga_mapping, verbose=True):
    layer_mapping = LayerMapping(model=LGA, data=filepath, mapping=mapping,
                                 transform=False, encoding='utf8')
    layer_mapping.save(verbose=verbose, strict=True)
