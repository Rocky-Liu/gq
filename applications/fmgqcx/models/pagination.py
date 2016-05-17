class pager_html(object):
    def __init__(self, uri, page_index, page_size, count, pager_width=3):
        self.__uri = uri
        self.__page_index = int(page_index) if int(page_index) > 0 else 1
        self.__page_size = page_size
        self.__pager_width = pager_width
        self.__count = count
        self.__maxpage = (count-1)/page_size + 1
    def __pager_uri(self, index):
        if self.__uri.find('page_index') + 1:
            return self.__uri.replace('page_index=' + str(self.__page_index), 'page_index=' + str(index))
        elif self.__uri.find('?') + 1:
            return self.__uri + '&page_index=' + str(index)
        else:
            return self.__uri + '?page_index=' + str(index)

    def create(self):
        indexes = [i for i in range(self.__page_index - self.__pager_width, self.__page_index) if i > 0]
        lis = []
        lis.append(LI(A('首页',_href=self.__pager_uri(1))))
        lis.extend([LI(A(i,_href=self.__pager_uri(i))) for i in indexes])
        lis.append(LI(A(self.__page_index,_href=self.__pager_uri(self.__page_index)),_class='active'))
        indexes = [i for i in range(self.__page_index + 1, self.__page_index + self.__pager_width + 1) if (i - 1) * self.__page_size < self.__count]
        lis.extend([LI(A(i,_href=self.__pager_uri(i))) for i in indexes])
        lis.append(LI(A('尾页',_href=self.__pager_uri(self.__maxpage))))
        opts = []
        for i in [10,20,50]:
            if i == self.__page_size:
                opts.append(OPTION(str(i), _selected='selected'))
            else:
                opts.append(OPTION(str(i)))
        html = DIV(DIV(SPAN('每页'),SELECT(_id='page-size',*opts),SPAN('个'),_class='page-sort'),
                    SPAN('共',SPAN(self.__count,_class='text-info'),'条记录'),
                    DIV(UL(*lis),_class='pagination'),
                    DIV(SPAN('前往'),INPUT(_type='text',_class='form-control input-sm',_placeholder='页码'),INPUT(_type='button',_class='btn btn-info',_value='跳转'),_class='goto-page pull-right'),
                    DIV(_style='clear:both;'),
                    _class='table-foot')
        return html

class pagination(object):
    def __init__(self, table, uri, page_index=1, page_size=None, orderby='id', descending=True, fields=None, **params):
        self.__table = table
        self.__orderby = orderby
        self.__descending = bool(descending)
        self.__uri = uri
        self.__page_index = int(page_index) if int(page_index) > 0 else 1
        self.__fields = fields
        self.__conditions = [[k, v, '=='] for k, v in params.iteritems() if v and v <> '']
        if page_size == None:
            if request.cookies.has_key('page_size'):
                self.__page_size = int(request.cookies['page_size'].value)
            else:
                self.__page_size = 10
        else:
            self.__page_size = int(page_size)
            response.cookies['page_size'] = page_size
            response.cookies['page_size']['expires'] = 365*24*3600
            response.cookies['page_size']['path'] = '/'

    @property
    def condition(self):
        return self.__conditions

    def __get_query(self):
        db = self.__table._db

        #begin 根据条件构造查询字符串query,及上下文变量env
        query = ''
        env = {'db': db, 'table': self.__table}
        i = 0
        for f, v, o  in self.__conditions:
            i = i + 1
            target = 'table.' + f
            if f.find('.') > 0 and db.has_key(f.split('.')[0]):
                target = 'db.' + f
            elif not self.__table.has_key(f):
                continue
            if o == 'like':
                query = query + ('&('+ target + '.like(\"%' + v + '%\"))')
            else:
                query = query + ('&('+ target + o + 'param' + str(i) + ')')
                env['param' + str(i)] = v
        query = query.strip('&')
        #end

        #begin 将查询字符串转化为可执行代码，即查询条件
        if query == '':
            query = self.__table
        else:
            query = eval(query, {}, env)
        #end

        return query

    def export(self, filename, *columns):
        response.headers['Content'] = 'application/vnd.ms-excel'
        response.headers['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        import xlwt
        import StringIO
        wb = xlwt.Workbook(encoding = 'utf-8')
        ws = wb.add_sheet('1')
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style = xlwt.XFStyle()
        style.alignment = alignment
        db = self.__table._db
        query = self.__get_query()
        if type(self.__orderby) == str:
            orderby = eval((('~' if self.__descending else '') + 'table.' + self.__orderby), {}, {'table': self.__table})
        else:
            orderby = self.__orderby
        rows = db(query).select(*[c[1] for c in columns], orderby = orderby)
        i=j=0
        for c in columns:
            ws.write(i,j,c[0])
            j = j + 1
        for row in rows:
            i = i + 1
            j = 0
            for c in columns:
                data = row[str(c[1])]
                if len(c) == 3:
                    data = c[2](data)
                ws.write(i,j,data,style)
                j = j + 1
        sio = StringIO.StringIO()
        wb.save(sio)
        return sio.getvalue()

    def pager(self):
        db = self.__table._db

        query = self.__get_query()

        count = db(query).count()
        if type(self.__orderby) == str:
            orderby = eval((('~' if self.__descending else '') + 'table.' + self.__orderby), {}, {'table': self.__table})
        else:
            orderby = self.__orderby
        #begin 如果当前页码大于最大页码，则自动重置为尾页
        maxpage = (count - 1)/self.__page_size + 1
        if maxpage == 0:
            self.__page_index = 1
        elif self.__page_index > maxpage:
            self.__page_index = maxpage
        #end

        limitby = ((self.__page_index-1)*self.__page_size, self.__page_index*self.__page_size)
        if self.__fields:
            rows = db(query).select(*self.__fields, orderby = orderby, limitby = limitby)
        else:
            rows = db(query).select(orderby = orderby, limitby = limitby)

        html = pager_html(self.__uri, self.__page_index, self.__page_size, count).create()

        return dict(rows = rows, count = count, html = html)
