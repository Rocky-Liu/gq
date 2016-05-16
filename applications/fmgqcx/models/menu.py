# ###########################################################
# ## generate menu
# ###########################################################

_a = request.application
_c = request.controller
_f = request.function
T.force('zh-cn')
response.title = 'FMGQCX信息查询系统'
_t = None
if request.vars.app or request.args:
    _t = request.vars.app or request.args[0]
if session.authorized:
    if session.auth.user.username == 'admin':
        response.menu = [('首页', _c == 'default', URL(_a, 'default', 'index', args=_t))]
        response.menu.append(('公告', _c == 'notice', URL(_a, 'notice', 'index', args=_t)))
        response.menu.append(('留言', _c == 'message', URL(_a, 'message', 'index', args=_t)))
        response.menu.append(('用户管理', _c == 'user', URL(_a, 'user', 'index', args=_t)))
    else:
        response.menu = [('首页', _c == 'default', URL(_a, 'default', 'my', args=_t))]
        response.menu.append(('公告', _c == 'notice', URL(_a, 'notice', 'list', args=_t)))
        response.menu.append(('留言', _c == 'message', URL(_a, 'message', 'show', args=_t)))
        response.menu.append(('修改资料', _c == 'user', URL(_a, 'user', 'me', args=_t)))

    response.menu.append((T('Logout'), False,
                          URL(_a, 'default', f='logout')))
