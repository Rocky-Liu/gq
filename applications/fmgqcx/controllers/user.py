@auth.requires_login()
def index():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    user_list = db(db.auth_user.username <> 'admin').select(db.auth_user.id,
                                                            db.auth_user.username,
                                                            db.auth_user.first_name,
                                                            db.auth_user.last_name,
                                                            db.auth_user.identity_card)
    return dict(user_list = user_list)

def me():
    pass

@auth.requires_login()
def add():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    form = SQLFORM(db.auth_user, fields = [
        'username', 'first_name', 'last_name', 'identity_card', 'password'])
    form.vars.password = db.auth_user.password.validate(form.vars.password)[0]
    if form.process(session=None, formname='form_add').accepted:
        session.flash = '添加成功'
        redirect('index')
    elif form.errors:
        response.flash = '表单验证失败'
    return dict(form = form)

@auth.requires_login()
def delete():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    user_id = int(request.args(0) or redirect(URL('index')))
    count = db(db.auth_user.id == user_id).delete()
    if count == 0:
        session.flash = '删除失败'
    else:
        session.flash = '删除成功'
        
    redirect(URL('index'))        

@auth.requires_login()
def edit():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    user_id = int(request.args(0) or redirect(URL('index')))
    record = db(db.auth_user.id == user_id).select().first()
    form = SQLFORM(db.auth_user, record, fields = [
        'username', 'first_name', 'last_name', 'identity_card'])
    if form.process(session=None, formname='form_edit').accepted:
        session.flash = '修改成功'
        redirect(URL('index'))
    elif form.errors:
        response.flash = '表单验证失败'
    return dict(form = form, record = record)

def reset():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    user_id = int(request.args(0) or redirect(URL('index')))
    record = db(db.auth_user.id == user_id).select().first()
    form = SQLFORM(db.auth_user, record, fields = ['password'])
    form.vars.password = db.auth_user.password.validate(form.vars.password)[0]
    if form.process(session=None, formname='form_edit').accepted:
        session.flash = '修改成功'
        redirect(URL('index'))
    elif form.errors:
        response.flash = '表单验证失败'
    return dict(form = form, record = record)

