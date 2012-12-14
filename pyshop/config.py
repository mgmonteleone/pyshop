#-*- coding: utf-8 -*-
from pyramid.interfaces import IBeforeRender
from pyramid.security import has_permission
from pyramid.url import static_path, route_path
# from pyramid.renderers import JSONP

from pyramid_jinja2 import renderer_factory

from pyshop.helpers import pypi
from pyshop.helpers.restxt import parse_rest
from pyshop.helpers.download import renderer_factory as dl_renderer_factory


def add_urlhelpers(event):
    """
    Add helpers to the template engine.
    """
    event['static_url'] = lambda x: static_path(x, event['request'])
    event['route_url'] = lambda name, *args, **kwargs: \
                            route_path(name, event['request'], *args, **kwargs)
    event['parse_rest'] = lambda x: parse_rest(x)
    event['has_permission'] = lambda perm: has_permission(perm,
                                    event['request'].context,
                                    event['request'])


def includeme(config):
    # config.add_renderer('json', JSONP())
    # release file download
    config.add_renderer('repository', dl_renderer_factory)

    # Jinja configuration
    # We don't use jinja2 filename, .html instead
    config.add_renderer('.html', renderer_factory)
    # helpers
    config.add_subscriber(add_urlhelpers, IBeforeRender)
    # i18n
    config.add_translation_dirs('locale/')

    # PyPI url for XML RPC service consume
    pypi.set_proxy(config.registry.settings['pypi.url'])

    # Javascript + Media
    config.add_static_view('static', 'static', cache_max_age=3600)
    #config.add_static_view('repository', 'repository', cache_max_age=3600)

    # Css
    config.add_route('css', '/css/{css_path:.*}.css')
    config.add_view(route_name=u'css', renderer=u'scss', request_method=u'GET',
        view=u'pyramid_scss.controller.get_scss')

    # Credentials
    config.add_view('pyshop.views.login',
                    renderer=u'shared/login.html',
                    context=u'pyramid.exceptions.Forbidden')

    config.add_view('pyshop.views.credentials.authbasic',
                    route_name='list_simple',
                    context='pyramid.exceptions.Forbidden'
                    )

    config.add_view('pyshop.views.credentials.authbasic',
                    route_name='show_simple',
                    context='pyramid.exceptions.Forbidden'
                    )

    config.add_route(u'login', u'/login',)
    config.add_view(u'pyshop.views.login',
                    route_name=u'login',
                    renderer=u'shared/login.html')

    config.add_route(u'logout', u'/logout')
    config.add_view(u'pyshop.views.logout',
                    route_name=u'logout',
                    permission=u'user_view')

    # Home page
    config.add_route(u'index', u'/')
    config.add_view(u'pyshop.views.index',
                    route_name=u'index',
                    permission=u'user_view')

    # Archive downloads
    config.add_route(u'repository',
                     u'/repository/{file_id}/{filename:.*}',
                     request_method=u'GET')
    config.add_view(u'pyshop.views.repository.get_release_file',
                    route_name=u'repository',
                    renderer=u'repository',
                    permission=u'download_releasefile')

    # Simple views used by pip

    #config.add_route(u'list_simple', u'/simple', request_method=u'GET')
    config.add_route(u'list_simple', u'/simple/', request_method=u'GET')

    config.add_view(u'pyshop.views.list_simple',
                    route_name=u'list_simple',
                    renderer=u'pyshop/simple/list.html',
                    permission=u"download_releasefile")

    config.add_route(u'show_simple', u'/simple/{package_name}/')
    config.add_view(u'pyshop.views.show_simple',
                    route_name=u'show_simple',
                    renderer=u'pyshop/simple/show.html',
                    permission=u'user_view')

    # Used by setup.py sdist upload

    config.add_route(u'upload_releasefile', u'/simple/',
                     request_method=u'POST')

    config.add_view(u'pyshop.views.list_simple',
                     route_name=u'upload_releasefile',
                     permission=u'upload_releasefile')

    # Web Services

    config.add_view('pyshop.views.xmlrpc.PyPI', name='pypi')

    # Backoffice Views

    config.add_route(u'list_package', u'/pyshop/package')
    config.add_view(u'pyshop.views.list_package',
                    route_name='list_package',
                    renderer=u'pyshop/package/list.html',
                    permission=u'user_view')

    config.add_route(u'show_package',
                     u'/pyshop/package/{package_name}')

    config.add_view(u'pyshop.views.show_package',
                    route_name=u'show_package',
                    renderer=u'pyshop/package/show.html',
                    permission=u'user_view')

