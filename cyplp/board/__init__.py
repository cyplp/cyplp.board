import logging

from pyramid.config import Configurator
from pyramid.security import Authenticated, Allow
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy

import pycouchdb

from cyplp.board.views import callback


class RootFactory(object):
    __acl__ = [
    (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        pass

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # support logging in python3
    logging.config.fileConfig(
        settings['logging.config'],
        disable_existing_loggers=False
    )
    config = Configurator(settings=settings, root_factory=RootFactory)


    my_session_factory = SignedCookieSessionFactory(settings['secret']) #
    config.set_session_factory(my_session_factory)                      #

    config.set_authentication_policy(AuthTktAuthenticationPolicy('plop',
                                                                 callback=callback,
                                                                 hashalg='sha512'))

    config.set_authorization_policy(ACLAuthorizationPolicy())

    for include in [
                    'pyramid_fanstatic',
                    'pyramid_chameleon',
                    'pyramid_mako',
                    'rebecca.fanstatic',
                  ]:
        config.include(include)


    server = pycouchdb.Server(settings['couchdb.uri'])
    config.registry.db = server.database(settings['couchdb.db'])

    def set_couchdb(request):
        return config.registry.db

    config.add_request_method(set_couchdb, 'db', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('admin', '/admin')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('board', '/board/{id}')
    config.add_route('addBoard', '/add/board')
    config.add_route('boardTitle', '/board/{id}/title')
    config.add_route('boardFull', '/board/{id}/full')
    config.add_route('boardConfig', '/board/{id}/config')
    config.add_route('boardCSS', '/board/{id}/css')
    config.add_route('addColumn', '/board/{id}/add/column')
    config.add_route('addItem', '/board/{idBoard}/column/{idColumn}/add/item')
    config.add_route('columnTitle', '/board/{idBoard}/column/{idColumn}/title')
    config.add_route('moveItem', '/board/{idBoard}/move/{idItem}')
    config.add_route('editItem', '/board/{idBoard}/edit/{idItem}')
    config.add_route('deleteItem', '/board/{idBoard}/delete/{idItem}')
    config.add_route('itemTitle', '/board/{idBoard}/edit/{idItem}/title')
    config.add_route('itemFull', '/board/{idBoard}/show/{idItem}/full')
    config.add_route('get_attachment', '/board/{idBoard}/edit/{idItem}/get/{attachment}')
    config.add_route('itemComment', '/board/{idBoard}/show/{idItem}/comment')
    config.add_route('uploadFile', '/board/{idBoard}/upload/{idItem}')
    config.add_route('editItemContent', '/board/{idBoard}/edit/{idItem}/content')
    config.add_route('saveItemContent', '/board/{idBoard}/save/{idItem}/content')
    config.add_route("account", "/account/{id}")
    config.add_route("updatepassword", "/account/{id}/password")

    config.scan()
    return config.make_wsgi_app()
