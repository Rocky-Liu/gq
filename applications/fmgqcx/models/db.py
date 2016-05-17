db = DAL('mysql://fmgqcp1v_root:rock4981@45.113.121.214/fmgqcp1v_gq', migrate_enabled=True)
db.define_table('gq',
	Field('no', 'string', length=16),
	Field('invest_type', 'string', length=32),
	Field('regist_share', 'integer'),
	Field('balance_share', 'integer'),
	Field('dividend_share', 'integer'),
	Field('bonus_share', 'integer'),
	Field('user_id', 'integer', notnull=True),
	Field('date', 'date')
)
db.define_table('notice',
            Field('title', 'string', length=128),
            Field('pub_time', 'datetime'),
            Field('content', 'string'),
            Field('user_id', 'integer')
)
db.define_table('message',
            Field('user_id', 'integer'),
            Field('pub_time', 'datetime'),
            Field('content', 'string'))
db.define_table('attachment',
                Field('attachment', 'upload')
                )
from gluon.tools import *
auth=Auth(db)
auth.settings.extra_fields['auth_user']= [
    Field('identity_card', 'string', length=18, label='身份证')]
auth.define_tables(username=True)
db.auth_user.username.requires = IS_NOT_IN_DB(db, db.auth_user.username)
auth.settings.login_url = URL('default', 'login')
if not session.authorized:
    if auth.user and not request.function == 'login':
        session.authorized = True
    elif not request.function == 'login':
        redirect(URL('default', 'login'))
