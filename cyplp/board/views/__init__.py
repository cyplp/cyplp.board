import logging
import datetime

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
# from pyramid.httpexceptions import HTTPBadRequest
from pyramid.events import subscriber
from pyramid.security import forget
from pyramid.security import remember

import bcrypt
import magic

from cyplp.board.rst_expression import RSTExpression
from cyplp.board.events import ItemMoved


from chameleon import PageTemplateFile
PageTemplateFile.expression_types['rst'] = RSTExpression


@subscriber(ItemMoved)
def something(event):
    print("evet !!")
    print(event.item)


@view_config(route_name='home', renderer="templates/home.pt", permission="authenticated")
def home(request):
    boards = request.db.query("board/all",
                               startkey=[request.session['login']],
                               endkey=[request.session['login'], {}])
    return {'boards': boards}


def validate(request, login, password):
    try:
        user = request.db.get(login)
    except couchdbkit.exceptions.ResourceNotFound:
        return False
    if bcrypt.hashpw(password.encode('utf-8'),
                     user['password']) != user['password']:
        return False

    request.session['login'] = login
    request.session['admin'] = user['admin']

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


@view_config(route_name="columnTitle", renderer="templates/column_title_form.pt",
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

@view_config(route_name="itemFull", renderer="templates/item.pt", request_method="GET", permission="authenticated")
@view_config(route_name="itemTitle", renderer="templates/item_title_form.pt",
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
@view_config(route_name="account", renderer="templates/account.pt",
             request_method="GET", permission="authenticated")
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

    user = request.db.get(request.matchdict['id'])

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

    user['password'] = password

    request.db.save(user)
    # todo flash
    return HTTPFound(location=request.route_path('account', id=user['_id']))

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

@view_config(route_name='uploadFile', request_method='POST', permission='authenticated')
def uploadFile(request):
    boardId = request.matchdict['idBoard']
    itemId = request.matchdict['idItem']

    item = request.db.get(itemId)

    files = []

    try:
        files.extend([item for item in request.POST.mixed().get('content')])
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
        request.session['login'] = login
        headers = remember(request, login)
        return HTTPFound(referrer, headers=headers)
    else:
        logging.info("%s failed", login)
        return HTTPFound(request.route_path('login'))

@view_config(route_name='logout', request_method='GET')
def logout(request):
    headers = forget(request)

    return HTTPFound(request.route_path('login'), headers=headers)
