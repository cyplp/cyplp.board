import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.events import subscriber, ApplicationCreated

from cyplp.board.models import Board
from cyplp.board.models import Column
from cyplp.board.models import Item


@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    registry = event.app.registry
    db = registry.db.get_or_create_db(registry.settings['couchdb.db'])
    Board.set_db(db)
    Column.set_db(db)
    Item.set_db(db)

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

    boardId = request.matchdict['id']
    board = Board.get(boardId)

    contents = request.db.view("board/content" ,
                              startkey=[boardId, 0],
                              endkey=[boardId, {}]).all()

    columns = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 0}

    for current in contents:
        if current['key'][1] == 1:
            tmp = current['value']

            if 'items' not in columns[tmp['column']]:
                columns[tmp['column']]['items'] = []

            columns[tmp['column']]['items'].append(tmp)

    return {'columns': columns,
            'board': board,
            }


@view_config(route_name="addColumn")
def addColumn(request):
    boardId = request.matchdict['id']
    title = request.POST.get('title', None)
    if title:
        column = Column(title=title.strip(), board=boardId.strip())
        column.save()

    return HTTPFound(location=request.route_path('board', id=boardId))

@view_config(route_name="addItem")
def addItem(request):
    boardId = request.matchdict['idBoard'].strip()
    columnId = request.matchdict['idColumn'].strip()

    title = request.POST.get('title', None)

    if title:
        item = Item(title=title.strip(),
                    board=boardId,
                    column=columnId)
        item.save()
    return HTTPFound(location=request.route_path('board', id=boardId))

@view_config(route_name='moveItem', renderer="json")
def moveItem(request):
    """
    """
    item = Item.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        if item.column == request.json_body['from']:
            item.column = request.json_body['to']
            item.save()
            return "ok"

    return "ko"

@view_config(route_name="editItem", renderer="templates/edit.pt")
def editItem(request):
    boardId = request.matchdict['idBoard']
    item = Item.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        return {'item': item}

    return HTTPFound(location=request.route_path('board', id=boardId))
