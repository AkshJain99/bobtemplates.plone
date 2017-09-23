# -*- coding: utf-8 -*-

from mrbob.bobexceptions import ValidationError
from bobtemplates.plone.base import base_prepare_renderer
from bobtemplates.plone.base import logger
from lxml import etree
import re


def post_theme_name(configurator, question, answer):
    regex = r'^\w+[a-zA-Z0-9 \.\-_]*\w$'
    if not re.match(regex, answer):
        msg = u"Error: '{0}' is not a valid themename.\n".format(answer)
        msg += u"Please use a valid name (like 'Tango' or 'my-tango.com')!\n"
        msg += u"At beginning or end only letters|diggits are allowed.\n"
        msg += u"Inside the name also '.-_' are allowed.\n"
        msg += u"No umlauts!"
        raise ValidationError(msg)
    return answer


def _update_configure_zcml(configurator):
    """ Add the theme to configure.zcml of the package.
    """
    namespaces = {'plone': 'http://namespaces.plone.org/plone'}
    nsprefix = "{{{0}}}".format(namespaces['plone'])
    file_name = u'configure.zcml'
    file_path = configurator.variables['package_folder'] +\
        '/' + file_name

    with open(file_path, 'r') as xml_file:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file, parser)
        tree_root = tree.getroot()
        theme_name = configurator.variables['theme.normalized_name']
        theme_xpath = "./plone:static[@name='{0}']".format(theme_name)
        if len(tree_root.xpath(theme_xpath, namespaces=namespaces)):
            print("%s already in configure.zcml, skip adding!" % theme_name)
            return
        etree.SubElement(
            tree_root,
            nsprefix + 'static',
            {'name': theme_name, 'directory': 'theme', 'type': 'theme'},
            nsmap=namespaces

        )

    with open(file_path, 'w') as xml_file:
        tree.write(
            xml_file, pretty_print=True, xml_declaration=True,
            encoding="utf-8")


def prepare_renderer(configurator):
    logger.info("Using plone_theme template:")
    configurator = base_prepare_renderer(configurator)
    configurator.variables['template_id'] = 'theme'

    def normalize_theme_name(value):
        value = "-".join(value.split('_'))
        value = "-".join(value.split())
        return value
    configurator.variables[
        "theme.normalized_name"] = normalize_theme_name(
            configurator.variables.get('theme.name')).lower()


def post_renderer(configurator):
    """
    """
    _update_configure_zcml(configurator)
    print("""
    Your theme is ready to go, but you want to make sure that the following
    packages are added to the ``install_requires`` list in your setup.py
    and run buildout after adding them:

     - collective.themesitesetup
     - collective.themefragments

    """)
