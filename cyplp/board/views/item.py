import logging
import datetime

import magic

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
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


@view_config(route_name="editItem", renderer="cyplp.board:templates/edit.pt", permission="authenticated")
def editItem(request):

    import rpdb
    rpdb.set_trace()

    boardId = request.matchdict['idBoard']
    item = request.db.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        return {'item': item}

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name="editItemContent", renderer="cyplp.board:templates/edit_content.pt",
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


@view_config(route_name="itemFull", renderer="cyplp.board:templates/item.pt", request_method="GET", permission="authenticated")
@view_config(route_name="itemTitle", renderer="cyplp.board:templates/item_title_form.pt",
             request_method="GET", permission="authenticated")
def itemTitleGet(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    # from chameleon import PageTemplateFile
    # PageTemplateFile.expression_types['rst'] = RSTExpression

    tmp = request.db.query("board/config" ,
                              startkey=[boardId, 0],
                              endkey=[boardId, {}])
    contents = [current for current in tmp]
    typeItems = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 0}
    tags = {current['value']['_id']: current['value'] for current in contents if current['key'][1] == 1}

    try:
        item = request.db.get(itemId)
    except: #  better exception 404.
        return HTTPNotFound()

    if 'content' not in item:
        item['content'] = ''

    return {'item': item,
            'typeItems': typeItems,
            'tags': tags,
           }

@view_config(route_name="get_attachment", request_method='GET', permission='authenticated')
def get_attachment(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)

    if item['board'] == boardId:

        response = request.response
        headers = response.headers

        headers['X-Accel-Redirect'] = str('/couch/'+itemId+'/get/'+request.matchdict['attachment'])

        return response
    else:
        return HTTPNotFound()

@view_config(route_name="itemTitle", request_method="POST", permission="authenticated")
def itemTitlePost(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)
    item['title'] = request.POST.get('title', '').strip()

    item['typeItem'] = request.POST.get('type', '')

    item['tags'] = request.POST.getall('tags')

    item['content'] = request.POST.get('content', '').strip()
    request.db.save(item)

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name="itemComment", request_method="POST", permission="authenticated")
def itemCommentPost(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)

    commentContent = request.POST.get('comment').strip()
    if commentContent:
        comment = {'content': commentContent,
                   'username': request.session['login'],
                   'dt_insert': datetime.datetime.now().isoformat()}

        if 'comments'  not in item:
            item['comments'] = []


        item['comments'].append(comment)

        request.db.save(item)

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name='uploadFile', request_method='POST', permission='authenticated')
def uploadFile(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)

    files = []

    try:
        files.extend([itemc for itemc in request.POST.mixed().get('content')])
    except TypeError:
        files.append(request.POST.mixed().get('content'))

    for file_ in files:
        filename = file_.filename
        mime = ''

        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as guess:
            mime = guess.id_buffer(file_.file.read(1024))
        file_.file.seek(0)

        request.db.put_attachment(item, file_.file, filename, mime)
        item = request.db.get(itemId)

    return HTTPFound(location=request.route_path('board', id=boardId))


@view_config(route_name="deleteItem", request_method="DELETE",
             permission="authenticated", renderer='json')
def deleteItem(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)

    if boardId != item.board:
        # TODO 404
        return {"status": "ko"}

    request.db.delete(item['_id'])

    return {"status": "ok"}
