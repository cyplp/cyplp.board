import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.events import subscriber, ApplicationCreated

from cyplp.board.models import Board



@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    registry = event.app.registry
    db = registry.db.get_or_create_db(registry.settings['couchdb.db'])
    Board.set_db(db)

@view_config(route_name='home', renderer="templates/home.pt")
def home(request):
    boards = request.db.view("board/all").all()

    return {'boards': boards}

@view_config(route_name="addBoard", request_method="POST")
def addBoard(request):
    title = request.POST.get('title', None)

    if title:
        board = Board(title=title,
                      owner='cyp')
        board.save()
        logging.info("%s board saved", title)

    return HTTPFound(location=request.route_path('home'))


@view_config(route_name='board', renderer='templates/board.pt')
def board(request):

    columns = [{'title': 'TODO',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Doing',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},

                {'title': 'Pause',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Done',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Nope',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]}

                ]

    return {'columns': columns,
            'board': {'name': 'my first board'},
            }
