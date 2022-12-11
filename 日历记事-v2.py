from tkinter import Tk,Frame,Label,Button,Spinbox,Text,messagebox
from datetime import datetime
from calendar import monthrange
import sqlite3


class DateFrame(Frame):
    def __init__(self,master,str_label,textColor=None ,cnf={}, **kw):
        super().__init__(master,cnf={}, **kw)
        self.grid_columnconfigure(1,weight=2)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=2)

        mBg=kw['bg']
        lbl=Label(self,text=str_label,bg=mBg,fg=textColor)
        lbl.grid(row=1,column=1,sticky='nw')

        mColor='tomato'

        btn=Button(self,text='+',fg=mColor,bg=mBg,borderwidth=0,activebackground=mColor,cursor='hand2')
        btn.grid(row=1,column=2,sticky='ne')

        txt=Text(self,fg=mColor,bg=mBg,height=6,borderwidth=0,
                highlightbackground=mBg,highlightcolor=mColor,highlightthickness=2,state='disable')

        txt.grid(row=2,column=1,columnspan=2,sticky='news')

        btn.bind('<Button-1>',lambda event:funAddOrSave(btn,lbl,txt))


def funAddOrSave(btn,lbl,txt):
    bg=btn.cget('bg')
    if btn.cget('text')=='+':
        btn.config(text='保存')
        txt.config(state='normal')
        txt.config(bg='lightyellow')
        txt.focus_set()
    else:
        btn.config(text='+')
        txt.config(state='disable')

        note_date=datetime.strptime(lbl.cget('text'), '%Y-%m-%d').date()

        myDb=MySqlite()

        result=myDb.executeQuery('select count(*) from t_dateNote where note_date=?',[note_date])

        num=result[0][0]

        str_note=txt.get('0.0','end').rstrip()

        if str_note.strip()!='':

            if num==0:
                print('插入数据')
                # 插入
                myDb.execute('insert into t_dateNote (note_date,note) values (?,?)',(note_date,str_note))
            else:
                print('更新数据')
                # 更新
                myDb.execute('update t_dateNote set note =? where note_date=?',(str_note,note_date))
        else:
            if num !=0: 
                print('删除数据')
                myDb.execute('delete from t_dateNote where note_date=?',[note_date])    # 删除

        txt.config(bg=bg)

        myDb.close()


def addWeekLabel(fm_date):
    # 日历星期标题
    list_week_label=['周一','周二','周三','周四','周五','周六','周日']
    len_list=len(list_week_label)

    for i in range(0,len_list):

        fm_date.grid_columnconfigure(i+1,weight=1)

        str_label = list_week_label[i]
        df=Frame(fm_date,bg='white')
        df.grid(column=i+1,row=1,sticky='news')
        Label(df,text=str_label,bg='white').pack(side='bottom')


def listDateFrame(dictValidate,list_df,fm_date):
    spb_year=dictValidate['spb_year']
    range_year=dictValidate['range_year']
    spb_month=dictValidate['spb_month']
    range_month=dictValidate['range_month']

    if funValidate(spb_year, range_year) and funValidate(spb_month, range_month):
        int_year=int(spb_year.get())
        int_month=int(spb_month.get())
        addDateFrame(list_df,int_year, int_month, fm_date)

        list_note(int_year,int_month,list_df)
    else:
        messagebox.showerror('日期错误','日期错误，请检查输入的年、月！')


def addDateFrame(list_df,int_year,int_month,fm_date):
    for df in list_df:
        df.destroy() # 销毁控件
    list_df.clear() # list_df是从外部传递来的，是引用传递，外部和内部一起变化（只要list_df不重新赋值，重新赋值会改变list的应用）

    li=monthrange(int_year, int_month)

    list_date=range(1,li[1]+1)
    myWeek=li[0]+1

    myRow=2

    str_nowDate=datetime.now().strftime('%Y-%m-%d')
    str_yearMonth=str(int_year)+'-'+str(int_month).rjust(2,'0')

    for d in list_date:

        bg='honeydew'
        if myWeek<6:
            bg='white'

        textColor=None

        str_date=str_yearMonth+'-'+str(d).rjust(2,'0')

        if str_date==str_nowDate:
            textColor='red'

        df=DateFrame(fm_date,str_label=str_date,textColor=textColor,relief='groove',bd=1,bg=bg)

        if myRow==2 or myWeek==1:
            fm_date.grid_rowconfigure(myRow,weight=1)

        df.grid(column=myWeek,row=myRow,sticky='news')

        list_df.append(df)

        if myWeek % 7 == 0:

            myRow+=1

            myWeek=0

        myWeek+=1


def list_note(int_year,int_month,list_df):

    str_yearMonth=str(int_year)+'-'+str(int_month).rjust(2,'0')
    
    strSql='select note_date,note from t_dateNote where note_date like ? order by note_date'
    parameter=[str_yearMonth +'%']

    myDb=MySqlite()
    result=myDb.executeQuery(strSql,parameter)
    myDb.close()

    if not result: return

    dict_result={r[0]:r[1] for r in result}
    # print(dict_result)
    
    dict_widget={}
    for df in list_df:
        list_widget=df.winfo_children()
        dict_widget[list_widget[0].cget('text')]=list_widget[2]

    for str_txt in dict_result:
        txt=dict_widget[str_txt]
        txt.config(state='normal')
        txt.insert('0.0',dict_result[str_txt])
        txt.config(state='disable')


def funValidate(spb,range_val):
    str_val=spb.get()
    errorMsg=''

    mBg='lightsalmon'

    try:
        int_val=int(str_val)
    except:
        errorMsg='错误，不是整数！'
        spb.config(bg=mBg)
        print(errorMsg)
        return False
 
    if int_val not in range_val:
        errorMsg='错误，超出范围！'

    if errorMsg:
        spb.config(bg=mBg)
        print(errorMsg)
        return False
    else:
        spb.config(bg='honeydew')
        return True


class MySqlite():
    def __init__(self):
        self.conn=sqlite3.connect('calendarNote.db')
        self.cursorObj=self.conn.cursor()
        strSql='create table if not exists t_dateNote(id integer primary key autoincrement, \
                                                        note_date date not null, \
                                                        note varchar not null);'
        self.createTable(strSql)

    def createTable(self,strSql):
        try:
            self.cursorObj.execute(strSql)
        except Exception as e:
            print(e)

    def executeQuery(self,strSql,*parameter):
        self.cursorObj.execute(strSql,*parameter)
        return self.cursorObj.fetchall()

    def execute(self,strSql,*parameter):
        try:
            self.cursorObj.execute(strSql,*parameter)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(e)

    def close(self):
        self.cursorObj.close()
        self.conn.close()

def exportData(spb_year,spb_month):

    str_year=spb_year.get().strip()
    str_month=spb_month.get().strip()

    strSql=''
    str_sql_common='select note_date,note from t_dateNote {} order by note_date'

    parameter=[]

    if str_year!='' and str_month!='':
        strSql=str_sql_common.replace('{}','where note_date like ?')
        str_month=str_month.rjust(2,'0')
        parameter=[str_year+'-'+str_month+'-%']
    elif str_year=='' and str_month=='':
        strSql=str_sql_common.replace('{}','')
    elif str_month=='':
        strSql=str_sql_common.replace('{}','where note_date like ?')
        parameter=[str_year+'-%']

    if strSql!='': 
        myDb=MySqlite()
        result=myDb.executeQuery(strSql,parameter)
        myDb.close()

        if result:
            # 写文件
            str_result='Note日期,Note记录\n'
            for r in result:
                str_result+=','.join(r)+'\n'

            fileName='export_date_note.csv'
            try:
                with open(fileName,'w') as f:
                    f.write(str_result)
            except Exception as e:
                print(e)
                messagebox.showerror('文件无法写入','同文件夹下的结果文件：' + fileName + '无法写入')
                return

            messagebox._show('导出成功','请查看同文件夹下的结果文件：\n      ' + fileName)
        else:
            messagebox.showinfo('无数据','无数据导出！')


def windowInit():
    mainWindow=Tk()
    mainWindow.title('日历记事')

    width_win = 800
    height_win = 600
    x_win = (mainWindow.winfo_screenwidth() // 2) - (width_win // 2)
    y_win = (mainWindow.winfo_screenheight() // 3) - (height_win // 3)

    # 窗口居中，设置 窗口大小、位置：字符串格式：width x height + x + y
    mainWindow.geometry('{}x{}+{}+{}'.format(width_win, height_win, x_win, y_win))

    fm_top=Frame(mainWindow,padx=4)
    fm_top.pack(fill='x')

    fm_top.grid_columnconfigure(1,weight=1)

    bg='honeydew'
    btn_export=Button(fm_top,text='导出',bg=bg)
    btn_export.grid(column=1,row=1,sticky='nw')
    
    fm_top.grid_columnconfigure(2,weight=2)
    fm_yearMonth=Frame(fm_top,padx=4)
    fm_yearMonth.grid(column=2,row=1,sticky='nw')

    my_side='left'

    Label(fm_yearMonth,width=20).pack(side=my_side)

    min_num=1900
    max_num=2100

    validate='focusout'
    justify='center'

    spb_year=Spinbox(fm_yearMonth,from_=min_num,to=max_num,validate=validate,width=6,justify=justify)
    spb_year.delete(0,'end')
    spb_year.insert(0,datetime.now().year)

    range_year=range(min_num,max_num+1)
    spb_year.config(validatecommand=lambda :funValidate(spb_year,range_year))
    spb_year.pack(side=my_side)

    Label(fm_yearMonth,text='年').pack(side=my_side)

    min_num_1=1
    max_num_1=12

    spb_month=Spinbox(fm_yearMonth,from_=min_num_1,to=max_num_1,validate=validate,width=4,justify=justify)

    spb_month.delete(0,'end')
    spb_month.insert(0,datetime.now().month)

    range_month=range(min_num_1,max_num_1+1)
    spb_month.config(validatecommand=lambda :funValidate(spb_month,range_month))

    spb_month.pack(side=my_side)

    Label(fm_yearMonth,text='月',width=2).pack(side=my_side)
    btn_goto=Button(fm_yearMonth,text='转到',bg=bg)
    btn_goto.pack(side=my_side)

    btn_export.bind('<Button-1>',lambda event: exportData(spb_year,spb_month))

    fm_date=Frame(mainWindow)
    fm_date.pack(fill='both',expand=True)

    # 星期
    addWeekLabel(fm_date)

    # 日期
    list_df=[]

    dictValidate={}
    dictValidate['spb_year']=spb_year
    dictValidate['range_year']=range_year
    dictValidate['spb_month']=spb_month
    dictValidate['range_month']=range_month

    listDateFrame(dictValidate,list_df,fm_date)

    # 鼠标事件lambda需要event参数
    btn_goto.bind('<Button-1>',lambda event: listDateFrame(dictValidate,list_df,fm_date))

    mainWindow.mainloop()

if __name__=='__main__':
    windowInit()