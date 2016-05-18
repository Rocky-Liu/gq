@auth.requires_login()
def index():
    if session.auth.user.username <> 'admin':
        redirect(URL('my'))
    result = db((db.gq.user_id == db.auth_user.id)).select(db.gq.id,
        db.gq.no,
        db.gq.invest_type,
        db.gq.regist_share,
        db.gq.balance_share,
        db.gq.dividend_share,
        db.gq.bonus_share,
        db.gq.date,
        db.auth_user.username,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.identity_card,
        orderby = ~db.gq.date|~db.gq.id)
    regist_total,balance_total,dividend_total,bonus_total=0,0,0,0
    for row in result:
        regist_total += row.gq.regist_share
        balance_total += row.gq.balance_share
        dividend_total += row.gq.dividend_share
        bonus_total += row.gq.bonus_share
    return dict(rows=result,
                regist_total=regist_total,
                balance_total=balance_total,
                dividend_total=dividend_total,
                bonus_total=bonus_total)

@auth.requires_login()
def add():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    form = SQLFORM(db.gq, fields = [
        'date', 'no', 'invest_type', 'regist_share', 'balance_share', 'dividend_share', 'bonus_share', 'user_id'])
    if form.process(session=None, formname='form_add').accepted:
        session.flash = '添加成功'
        redirect('index')
    elif form.errors:
        response.flash = '表单验证失败'
    user_list = db(db.auth_user.username<>'admin').select(db.auth_user.id,
                                                          db.auth_user.username,
                                                          db.auth_user.first_name,
                                                          db.auth_user.last_name)
    return dict(form = form, user_list = user_list)

@auth.requires_login()
def edit():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    gq_id = int(request.args(0) or redirect(URL('index')))
    record = db(db.gq.id == gq_id).select().first()
    form = SQLFORM(db.gq, record, fields = [
         'date', 'no', 'invest_type', 'regist_share', 'balance_share', 'dividend_share', 'bonus_share', 'user_id'])
    if form.process(session=None, formname='form_edit').accepted:
        session.flash = '修改成功'
        redirect(URL('index'))
    elif form.errors:
        response.flash = '表单验证失败'
    user_list = db(db.auth_user.username<>'admin').select(db.auth_user.id,
                                                          db.auth_user.username,
                                                          db.auth_user.first_name,
                                                          db.auth_user.last_name)
    return dict(form = form, record = record, user_list = user_list)

@auth.requires_login()
def delete():
    if session.auth.user.username <> 'admin':
        raise HTTP(404)
    gq_id = int(request.args(0) or redirect(URL('index')))
    count = db(db.gq.id == gq_id).delete()
    if count == 0:
        session.flash = '删除失败'
    else:
        session.flash = '删除成功'
    redirect(URL('index'))

@auth.requires_login()
def my():
    user = session.auth.user
    rows = db(db.gq.user_id == user.id).select(orderby=~db.gq.id)
    regist_total,balance_total,dividend_total,bonus_total=0,0,0,0
    for row in rows:
        regist_total += row.regist_share
        balance_total += row.balance_share
        dividend_total += row.dividend_share
        bonus_total += row.bonus_share

    return dict(user=user,
                rows=rows,
                regist_total=regist_total,
                balance_total=balance_total,
                dividend_total=dividend_total,
                bonus_total=bonus_total)

def login():
    return dict(form = auth.login())

def logout():
    return dict(form=auth.logout())

@auth.requires_login()
def add_attachment():
    attachment_fields = ['attachment']
    form = SQLFORM(db.attachment, fields=attachment_fields)
    return_dict = {}
    if form.process(session=None, formname='attachment').accepted:
        # 如果插入成功，后台再插入一些需要数据
        id = form.vars.id
        if request.vars.attachment != None:
            return_dict['success'] = True
            return_dict['file_path'] = URL('default','download/%s'%db.attachment[id].attachment)
            return response.json(return_dict)
    elif form.errors:
        return_dict['success'] = False
        response.flash = 'form has errors'
        return response.json(return_dict)
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@cache.action()
def download():
    return response.download(request, db)
