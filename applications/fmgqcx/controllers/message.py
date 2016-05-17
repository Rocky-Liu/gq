@auth.requires_login()
def index():
    is_admin=False
    if session.auth.user.username == 'admin':
        is_admin = True
    result = db(db.message.user_id == db.auth_user.id).select(db.message.ALL,
                                                              db.auth_user.last_name,
                                                              db.auth_user.first_name, orderby = ~db.message.pub_time)
    return dict(rows=result, is_admin=is_admin)

@auth.requires_login()
def add():
    form = SQLFORM(db.message, fields = ['content'])
    form.vars.pub_time = datetime.now()
    form.vars.user_id = session.auth.user.id
    if form.process(session=None, formname='form_add').accepted:
        session.flash = '留言成功'
        redirect('index')
    elif form.errors:
        session.flash = '留言失败'
        redirect('index')
    return dict(form = form)


@auth.requires_login()
def delete():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    message_id = int(request.args(0) or redirect(URL('index')))
    count = db(db.message.id == message_id).delete()
    if count == 0:
        session.flash = '删除失败'
    else:
        session.flash = '删除成功'

    redirect(URL('index'))

