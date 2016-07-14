import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


@view_config(route_name="addBoard", request_method="POST", permission="authenticated")
def addBoard(request):
    title = request.POST.get('title', None)
    owner = request.session['login']

    if title:
        doc = request.db.save({'title': title,
                               'owner': owner,
                               'doc_type': 'Board'})

        logging.info("%s board saved on %s", title, doc['_id'])

    return HTTPFound(location=request.route_path('home'))


@view_config(route_name='board', renderer='templates/board.pt', permission="authenticated")
def board(request):

    boardId = request.matchdict['id']
    board = request.db.get(boardId)

    tmp = request.db.query("board/content" ,
                           startkey=[boardId, 0],
                           endkey=[boardId, {}])

    contents = [current for current in tmp]

    columns = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 0}
    typeItems = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 2}
    tags = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 3}

    for current in contents:
        if current['key'][1] == 1:
            tmp = current['value']

            if 'items' not in columns[tmp['column']]:
                columns[tmp['column']]['items'] = []

            columns[tmp['column']]['items'].append(tmp)

    return {'columns': columns,
            'board': board,
            'typeItems': typeItems,
            'tags': tags,
            }


@view_config(route_name="addColumn", permission="authenticated")
def addColumn(request):
    boardId = request.matchdict['id']
    title = request.POST.get('title', None)
    if title:
        column = {'title': title.strip(),
                  'board': boardId.strip(),
                  'doc_type': 'Column'}
        request.db.save(column)

    return HTTPFound(location=request.route_path('board', id=boardId))
