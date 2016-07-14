import logging

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.events import subscriber
from pyramid.security import forget
from pyramid.security import remember

import bcrypt

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
