eha-nutsurv-django
==================

NutSurv - Data collection and quality assurance tools for Nutrition Surveys on mobile devices


# Install with Docker

Install [Docker](https://docs.docker.com/installation/#installation)

## Tab 1

    $ git clone git@github.com:eHealthAfrica/eha-nutsurv-django.git
    $ sudo apt-get install python-pip
    $ sudo pip install -U docker-compose
    $ cd eha-nutsurv-django/
    $ sudo docker-compose build


## Tab 2

    $ sudo docker-compose run db

## Tab 1 again

    $ sudo docker-compose run web bash

Now in the shell within the container:

    # python /opt/nutsurv/nutsurv/manage.py migrate
    # python /opt/nutsurv/nutsurv/manage.py createsuperuser
    # python /opt/nutsurv/nutsurv/manage.py bower_install -- --allow-root
    # python /opt/nutsurv/nutsurv/manage.py runserver 0.0.0.0:8001


## Good job!
The website should be available at http://HOST:8001


## Preload GIS data

After the system has been installed and configured you might want to load some geographic data set with LGAs instead of adding them via the Django admin site.  Please continue reading this section.

### Example GIS data

In case you do not have your own shapefile, the shapefile used for testing has been downloaded from http://www.diva-gis.org/gdata by selecting 'Nigeria' from the drop-down list of countries and 'Administrative areas' from the drop-down list of subjects.  The thus acquired NGA_adm.zip file was then unzipped and the Nigerian LGA level data was imported (see below for instructions) from the NGA_adm2.shp file (which was one of the files contained in the downloaded archive).


### Simple scenario

In order to preload the database with some LGA data, copy the shapefile (e.g. somefile.shp + somefile.shx + somefile.dbf) you want to use to the directory of your choosing, invoke the Django shell:

    $ path/to/the/manage.py shell

WARNING: This scenario assumes that the shapefile you prepared is compatible with the default mapping dictionary defined in the load module.  If it is not, check the optional steps described later in the 'Custom mapping dictionary' section.  As of this writing, the shapefile mentioned in section 'Example GIS data' above is compatible and importing it does not require any additional steps.

Next, import the load module and call the import_data_from_file function passing the path to your .shp file as an argument:

    >>> import dashboard.load
    >>> dashboard.load.import_data_from_file('/path/to/your/shapefile.shp')

After the function finishes, exit the shell and enjoy all those newly added LGAs.

### Custom mapping dictionary

The default mapping dictionary defined in the load module assumes that the shapefile has the following attribute fields:

* NAME_0 - which stores the name of the top-level area (e.g. a country)
* NAME_1 - which stores the name of the mid-level area (e.g. a state)
* NAME_2 - which stores the name of the area of interest (e.g. an LGA) - i.e. the area contained by the mid-level area (which in turns is contained by the top-level area)
* VARNAME_2 - an alternative name of the area of interest (optional, can be NULL)

Since the LGA model defines the following fields: name_0, name_1, name_2, varname_2, mpoly, the attribute fields of the shapefile have to be mapped to the fields of the LGA model by defining the following dictionary (do not worry about the mpoly mapping, just remember to always have it in your mapping dictionary):

    $ path/to/the/manage.py shell

    >>> some_mapping_dictionary = {
    >>>     'name_0': 'NAME_0',
    >>>     'name_1': 'NAME_1',
    >>>     'name_2': 'NAME_2',
    >>>     'varname_2': 'VARNAME_2',
    >>>     'mpoly': 'MULTIPOLYGON',
    >>> }

Now, when you have defined your new dictionary, you can use it and load your GIS data:

    >>> import dashboard.load
    >>> dashboard.load.import_data_from_file(filepath='/path/to/your/shapefile.shp',
                                             mapping=some_mapping_dictionary)



===================

# Override settings

You can override settings by adding a file named "configuration.py" to the root of the project. See configuration.py-default for an example.
