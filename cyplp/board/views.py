from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):

    columns = [{'title': 'TODO',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Doing',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},

                {'title': 'Pause',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Done',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]},
                {'title': 'Nope',
                '_id': 'ertyuiop',
                'items': [{'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'},
                           {'title': 'item1',
                           'content': 'rtyuibn,isdfsdfefdsfsdfd'}]}

                ]

    return {'columns': columns,
            'board': {'name': 'my first board'},
            }
