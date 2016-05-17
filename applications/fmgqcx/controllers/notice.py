@auth.requires_login()
def index():
    is_admin=False
    if session.auth.user.username == 'admin':
        is_admin = True
    result = db(db.notice.user_id==db.auth_user.id).select(db.notice.id,
                                                           db.notice.title,
                                                           db.notice.pub_time,
                                                           db.auth_user.last_name,
                                                           db.auth_user.first_name)
    return dict(rows=result, is_admin=is_admin)

@auth.requires_login()
def add():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    form = SQLFORM(db.notice, fields = [
        'title', 'content'])
    form.vars.pub_time = datetime.now()
    form.vars.user_id = session.auth.user.id
    if form.process(session=None, formname='form_add').accepted:
        session.flash = '添加成功'
        redirect('index')
    elif form.errors:
        response.flash = '表单验证失败'
    return dict(form = form)


@auth.requires_login()
def edit():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    notice_id = int(request.args(0) or redirect(URL('index')))
    record = db(db.notice.id == notice_id).select().first()
    form = SQLFORM(db.notice, record, fields = ['title', 'content'])
    if form.process(session=None, formname='form_edit').accepted:
        session.flash = '修改成功'
        redirect(URL('index'))
    elif form.errors:
        response.flash = '表单验证失败'
    return dict(form = form, record = record)


@auth.requires_login()
def delete():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    notice_id = int(request.args(0) or redirect(URL('index')))
    count = db(db.notice.id == notice_id).delete()
    if count == 0:
        session.flash = '删除失败'
    else:
        session.flash = '删除成功'

    redirect(URL('index'))


@auth.requires_login()
def show():
    notice_id = int(request.args(0) or redirect(URL('index')))
    result = db((db.notice.id == notice_id)&(db.notice.user_id==db.auth_user.id)).select(db.notice.ALL,
                                                                                         db.auth_user.last_name,
                                                                                         db.auth_user.first_name).first()
    return dict(result=result)
