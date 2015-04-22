from pyramid.config import Configurator
from pyramid.security import Authenticated, Allow
from pyramid.session import SignedCookieSessionFactory
from couchdbkit import Server


class RootFactory(object):
    __acl__ = [
    (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        pass

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=RootFactory)

    my_session_factory = SignedCookieSessionFactory(settings['secret'])
    config.set_session_factory(my_session_factory)

    for include in ['pyramid_fanstatic',
                    'pyramid_chameleon',
                    'pyramid_mako',
                    'rebecca.fanstatic',
                    'pyramid_auth',]:
        config.include(include)

    config.registry.db = Server(uri=settings['couchdb.uri'])

    def add_couchdb(request):
        db = config.registry.db.get_or_create_db(settings['couchdb.db'])
        return db

    config.add_request_method(add_couchdb, 'db', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('admin', '/admin')
    config.add_route('board', '/board/{id}')
    config.add_route('addBoard', '/add/board')
    config.add_route('boardTitle', '/board/{id}/title')
    config.add_route('boardConfig', '/board/{id}/config')
    config.add_route('boardCSS', '/board/{id}/css')
    config.add_route('addColumn', '/board/{id}/add/column')
    config.add_route('addItem', '/board/{idBoard}/column/{idColumn}/add/item')
    config.add_route('columnTitle', '/board/{idBoard}/column/{idColumn}/title')
    config.add_route('moveItem', '/board/{idBoard}/move/{idItem}')
    config.add_route('editItem', '/board/{idBoard}/edit/{idItem}')
    config.add_route('itemTitle', '/board/{idBoard}/edit/{idItem}/title')
    config.add_route('editItemContent', '/board/{idBoard}/edit/{idItem}/content')
    config.add_route('saveItemContent', '/board/{idBoard}/save/{idItem}/content')
    config.add_route("account", "/account/{id}")
    config.add_route("updatepassword", "/account/{id}/password")

    config.add_fanstatic_resources(['css.fontawesome.fontawesome',
                                    ], r'.*\.pt')

    config.scan()
    return config.make_wsgi_app()
