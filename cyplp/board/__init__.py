from pyramid.config import Configurator

from couchdbkit import Server



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    for include in ['pyramid_fanstatic',
                    'pyramid_chameleon',
                    'rebecca.fanstatic', ]:
        config.include(include)

    config.registry.db = Server(uri=settings['couchdb.uri'])

    def add_couchdb(request):
        db = config.registry.db.get_or_create_db(settings['couchdb.db'])
        return db

    config.add_request_method(add_couchdb, 'db', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('board', '/board/{id}')
    config.add_route('addBoard', '/add/board')

    config.add_fanstatic_resources(['css.fontawesome.fontawesome',
                                    ], r'.*\.pt')

    config.scan()
    return config.make_wsgi_app()
