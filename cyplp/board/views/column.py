from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound


@view_config(route_name="columnTitle", renderer="cyplp.board:templates/column_title_form.pt",
             request_method="GET", permission="authenticated")
def columnTitleGet(request):
    boardId = request.matchdict['idBoard']
    columnId = request.matchdict['idColumn']

    column = request.db.get(columnId)

    return {'column': column}

@view_config(route_name="columnTitle", request_method="POST", permission="authenticated")
def columnTitlePost(request):
    boardId = request.matchdict['idBoard']
    columnId = request.matchdict['idColumn']

    column = request.db.get(columnId)
    column['title'] = request.POST.get('title')

    request.db.save(column)

    return HTTPFound(location=request.route_path('board', id=boardId))


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
