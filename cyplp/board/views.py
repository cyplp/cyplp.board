import logging

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.security import forget
from pyramid.security import remember
import bcrypt
#import couchdbkit


# from cyplp.board.models import Board
# from cyplp.board.models import Column
# from cyplp.board.models import Item
# from cyplp.board.models import TypeItem
# from cyplp.board.models import User
# from cyplp.board.models import Tag

from cyplp.board.rst_expression import RSTExpression

# @subscriber(ApplicationCreated)
# def application_created_subscriber(event):
#     registry = event.app.registry
#     db = registry.db.get_or_create_db(registry.settings['couchdb.db'])

#     for schema in [Board, Column, Item, TypeItem, User, Tag]:
#         schema.set_db(db)

@view_config(route_name='home', renderer="templates/home.pt", permission="authenticated")
def home(request):
    boards = request.db.query("board/all")

    return {'boards': boards}

@view_config(route_name="addBoard", request_method="POST", permission="authenticated")
def addBoard(request):
    title = request.POST.get('title', None)

    # TODO userid
    owner = 'cyp'

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

    from chameleon import PageTemplateFile
    PageTemplateFile.expression_types['rst'] = RSTExpression

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

@view_config(route_name='moveItem', renderer="json", permission="authenticated")
def moveItem(request):
    """
    """
    # TODO schema ?
    item = request.db.get(request.matchdict['idItem'])

    from_ = request.json_body.get('from')
    to = request.json_body.get('to')

    if not from_ or not to:
        return HTTPBadRequest("missing from or to")
    if item['board'] == request.matchdict['idBoard']:
        if item['column'] == from_:
            item['column'] = to
            request.db.save(item)
            return "ok"

    return "ko"

@view_config(route_name="editItem", renderer="templates/edit.pt", permission="authenticated")
def editItem(request):
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

@view_config(route_name="editItemContent", renderer="templates/edit_content.pt",
             request_method="POST", permission="authenticated")
def editItemContentPost(request):
    item = Item.get(request.matchdict['idItem'])

    if item.board == request.matchdict['idBoard']:
        item.content = request.POST.get('content', '')
        item.save()

    return HTTPFound(location=request.route_path('editItem',
                                                 idBoard=request.matchdict['idBoard'],
                                                 idItem=request.matchdict['idItem']))


def validate(request, login, password):
    try:
        user = User.get(login)
    except couchdbkit.exceptions.ResourceNotFound:
        return False
    if bcrypt.hashpw(password.encode('utf-8'),
                     user.password) != user.password:
        return False

    request.session['login'] = login
    request.session['admin'] = user.admin

    return True

def callback(uid, *args, **kw):
    return []

@view_config(route_name='admin', renderer="templates/admin.pt", request_method="GET", permission="authenticated")
def admin(request):
    users = request.db.view("user/all").all()
    return {"users": users }

@view_config(route_name='admin', request_method="POST", permission="authenticated")
def adminPost(request):
    login = request.POST.get('login')
    password = request.POST.get('password')
    name = request.POST.get('name', '')

    if not login or not password:
        return HTTPFound(location=request.route_path('admin'))

    password = bcrypt.hashpw(password.encode('utf-8'),
                             bcrypt.gensalt())

    try:
        User.get(login)
    except couchdbkit.exceptions.ResourceNotFound:
        user = User(_id=login, password=password, name=name)
        user.save()

    return HTTPFound(location=request.route_path('admin'))

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

@view_config(route_name="columnTitle", renderer="templates/column_title_form.pt", request_method="GET", permission="authenticated")
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

@view_config(route_name="itemTitle", renderer="templates/item_title_form.pt", request_method="GET", permission="authenticated")
def itemTitleGet(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']


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

    return {'item': item,
            'typeItems': typeItems,
            'tags': tags,
           }


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


@view_config(route_name="account", renderer="templates/account.pt", request_method="GET", permission="authenticated")
def accountGET(request):
    user = request.db.get(request.matchdict['id'])
    return {'user': user}

@view_config(route_name="account", request_method="POST", permission="authenticated")
def accountPOST(request):

    user = request.db.get(request.matchdict['id'])
    user['name'] = request.POST.get('name', '').strip()
    request.db.save(user)

    return HTTPFound(location=request.route_path('account', id=user['_id']))


@view_config(route_name="updatepassword", request_method="POST", permission="authenticated")
def updatepasswordPOST(request):

    user = User.get(request.matchdict['id'])

    old = request.POST.get("old_password")
    password = request.POST.get("password")
    repeat = request.POST.get("repeat")

    if not password:
        # todo flash
        print("empty password")
        return HTTPFound(location=request.route_path('account', id=user['_id']))

    if not (password == repeat):
        # todo flash
        print("mismatch password")
        return HTTPFound(location=request.route_path('account', id=user['_id']))

    if not validate(request, user._id, old):
        # todo flash
        print("old one password")
        return HTTPFound(location=request.route_path('account', id=user['_id']))

    password = bcrypt.hashpw(password.encode('utf-8'),
                             bcrypt.gensalt())

    user.password = password

    user.save()
    # todo flash
    return HTTPFound(location=request.route_path('account', id=user['_id']))

@view_config(route_name="boardConfig", request_method="GET",
             permission="authenticated", renderer="templates/board_config.pt")
def boardConfigGet(request):
    boardId = request.matchdict['id']

    board = Board.get(boardId)
    contents = request.db.view("board/config" ,
                              startkey=[boardId, 0],
                              endkey=[boardId, {}]).all()

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
        if request.POST.get('form', 'type') == 'type':
            typeItem = TypeItem(name=name,
                                color=color,
                                board=boardId)
            typeItem.save()
        else:
            tag = Tag(name=name,
                color=color,
                board=boardId)
            tag.save()

    return HTTPFound(location=request.route_path('boardConfig', id=boardId))


@view_config(route_name="boardCSS", request_method="GET",
             permission="authenticated")
def boardCSS(request):
    boardId = request.matchdict['id']

    contents = request.db.query("board/config" ,
                              startkey=[boardId, 0],
                              endkey=[boardId, {}])

    typeItems = [".type_%s {background-color: %s;}" % (current['value']['_id'], current['value']['color'])
                 for current in contents if current['key'][1] == 0]

    tags = [".tag_%(_id)s {background-color: %(color)s;}" % {key: value for key, value in current['value'].iteritems()}
                 for current in contents if current['key'][1] == 1]

    response = request.response

    response.text = '\n'.join(["\n".join(typeItems), "\n".join(tags)])

    response.content_type = 'text/css'
    return response


@view_config(route_name="deleteItem", request_method="DELETE",
             permission="authenticated", renderer='json')
def deleteItem(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = Item.get(itemId)

    if boardId != item.board:
        # TODO 404
        return {"status": "ko"}

    item.delete()
    return {"status": "ok"}

@view_config(route_name='login', request_method='GET', renderer="templates/login.pt")
@forbidden_view_config(renderer='templates/login.pt')
def loginGet(request):
    return {}

@view_config(route_name='login', request_method='POST')
def loginPost(request):
    login = request.POST.get("login", '')
    password = request.POST.get("password", '')

    login_path = request.route_url('login')
    referrer = request.environ['HTTP_REFERER'] #  security issue ?

    if referrer == login_path:
        referrer = '/'

    if (validate(request, login, password)):
        logging.info("%s logged", login)
        headers = remember(request, login)
        return HTTPFound(referrer, headers=headers)
    else:
        logging.info("%s failed", login)
        return HTTPFound(request.route_path('login'))

@view_config(route_name='logout', request_method='GET')
def logout(request):
    headers = forget(request)

    return HTTPFound(request.route_path('login'), headers=headers)
