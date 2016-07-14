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


@view_config(route_name="boardTitle", renderer="templates/board_title_form.pt", request_method="GET", permission="authenticated")
def boardTitleGet(request):
    boardId = request.matchdict['id']
    board = request.db.get(boardId)

    return {'board': board}


@view_config(route_name="boardTitle", request_method="POST", permission="authenticated")
def boardTitlePost(request):
    boardId = request.matchdict['id']
    board = request.db.get(boardId)

    if request.POST.get('title'):
        board['title'] = request.POST.get('title')
        request.db.save(board)

    return HTTPFound(location=request.route_path('board', id=board['_id']))

@view_config(route_name="boardConfig", request_method="GET",
             permission="authenticated", renderer="templates/board_config.pt")
def boardConfigGet(request):
    boardId = request.matchdict['id']

    board = request.db.get(boardId)
    contents = [current for current in request.db.query("board/config",
                                                        startkey=[boardId, 0],
                                                        endkey=[boardId, {}])]


    typeItems = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 0}
    tags = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 1}

    return {'board': board,
            'typeItems': typeItems,
            'tags': tags}

@view_config(route_name="boardConfig", request_method="POST",
             permission="authenticated")
def boardConfigPost(request):
    boardId = request.matchdict['id']

    name = request.POST.get('name')
    color = request.POST.get('color', '#FFFFFF')

    if name:
        configItem = {'doc_type': 'TypeItem',
                        'name': name,
                        'color': color,
                        'board': boardId,}

        if request.POST.get('form', 'type') == 'type':
            configItem['doc_type'] = 'TypeItem'
        else:
            configItem['doc_type'] = 'Tag'

        request.db.save(configItem)

    return HTTPFound(location=request.route_path('boardConfig', id=boardId))


@view_config(route_name="boardCSS", request_method="GET",
             permission="authenticated")
def boardCSS(request):
    boardId = request.matchdict['id']

    contents = [current for current in request.db.query("board/config" ,
                                                        startkey=[boardId, 0],
                                                        endkey=[boardId, {}])]

    typeItems = [".type_%s {background-color: %s;}" % (current['value']['_id'], current['value']['color'])
                 for current in contents if current['key'][1] == 0]

    tags = [".tag_%(_id)s {background-color: %(color)s;}" % current['value']
                 for current in contents if current['key'][1] == 1]

    response = request.response

    response.text = '\n'.join(["\n".join(typeItems), "\n".join(tags)])

    response.content_type = 'text/css'
    return response
