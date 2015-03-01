import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.events import subscriber, ApplicationCreated

from cyplp.board.models import Board
from cyplp.board.models import Column



@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    registry = event.app.registry
    db = registry.db.get_or_create_db(registry.settings['couchdb.db'])
    Board.set_db(db)
    Column.set_db(db)

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

    columns = request.db.view("column/by_board",
                              startkey=boardId,
                              endkey=boardId).all()


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
