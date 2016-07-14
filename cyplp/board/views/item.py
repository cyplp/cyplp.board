import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest

from cyplp.board.events import ItemMoved


@view_config(route_name="addItem", permission="authenticated")
def addItem(request):
    boardId = request.matchdict['idBoard'].strip()
    columnId = request.matchdict['idColumn'].strip()

    title = request.POST.get('title', None)

    if title:
        item = {'title': title.strip(),
                'board': boardId,
                'column': columnId,
                'content': '',
                'doc_type': 'Item',
                }
        request.db.save(item)

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name='moveItem', renderer='json', permission='authenticated')
def moveItem(request):
    """
    """
    logging.info("here 0")

    item = request.db.get(request.matchdict['idItem'])
    from_ = request.json_body.get('from')

    to = request.json_body.get('to')


    if not from_ or not to:
        return HTTPBadRequest("missing from or to")

    if item['board'] == request.matchdict['idBoard']:
        if item['column'] == from_:
            item['column'] = to
            request.db.save(item)

            request.registry.notify(ItemMoved(item, to, from_))
            return "ok"

    return "ko"


@view_config(route_name="editItem", renderer="templates/edit.pt", permission="authenticated")
def editItem(request):

    import rpdb
    rpdb.set_trace()

    boardId = request.matchdict['idBoard']
    item = request.db.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        return {'item': item}

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name="editItemContent", renderer="templates/edit_content.pt",
             request_method="GET", permission="authenticated")
def editItemContentGet(request):
    item = request.db.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        return {'item': item}

# @view_config(route_name="editItemContent", renderer="templates/edit_content.pt",
#              request_method="POST", permission="authenticated")
# def editItemContentPost(request):
#     item = Item.get(request.matchdict['idItem'])

#     if item.board == request.matchdict['idBoard']:
#         item.content = request.POST.get('content', '')
#         item.save()

#     return HTTPFound(location=request.route_path('editItem',
#                                                  idBoard=request.matchdict['idBoard'],
#                                                  idItem=request.matchdict['idItem']))
