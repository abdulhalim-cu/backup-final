# -*- coding: utf-8 -*-
import gluon.contrib.simplejson as json
from datetime import datetime, timedelta
from time import localtime, strftime
import calendar
import pytz
import uuid

def cron_test():
    date = datetime.now().date()
    time = datetime.now().time().strftime('%H:%M:%S')
    db.cron_job.insert(request_date=date,request_time=time)
    db.commit()
    return dict()

def editedUsers():

    return dict()

def login():
    redirect(URL('default','user/login'))
    #auth.settings.login_after_registration = True
    return dict()

def append_dic(dic, key, value):
    dic.setdefault(key,[]).append(value)

#@auth.requires_login()
def index():
    if not auth.user:
        redirect(URL('user/login'))
    rows = db(db.auth_user.id==auth.user_id).select(db.auth_user.ALL)
    cid = "%(client_id)s" % auth.user
    query = db(db.Client_Unit.client_id==cid).select(db.Client_Unit.unit_id)
    return dict(query = query, cid=cid, rows=rows)

@auth.requires_login()
def log_today():
    if not auth.user:
        redirect(URL('user/login'))

    rows = db(db.auth_user.id==auth.user_id).select(db.auth_user.ALL)
    cid = "%(client_id)s" % auth.user
    query = db(db.Client_Unit.client_id==cid).select(db.Client_Unit.unit_id)
    return dict(query = query, cid=cid, rows=rows)

@auth.requires_login()
def usermanagement():
    if not auth.user:
        redirect(URL('login'))
    else:
        client_id = "%(client_id)s" % auth.user
        client_user = db(db.Client_User.client_id==client_id).select()
        ClientUnits = db(db.Client_Unit.client_id==client_id).select(db.Client_Unit.unit_id)
        totalUnits = len(ClientUnits)
    return dict(client_id=client_id,client_user=client_user,ClientUnits=ClientUnits,totalUnits=totalUnits)
@auth.requires_login()
def change_access():
    data = request.post_vars
    i = 0
    a = dict()
    while len(data['access']) > i:
        unit_id = data['unit_id'][i]
        user_id = data['user_id'][i]
        user_name=data['user_name'][i]
        access = data['access'][i]
        uid = data['uuid'][i]
        accs = db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.uuid==uid)).select(db.Unit_Users.access_type)
        if accs:
            for ac in accs:
                if access != ac.access_type:
                    db.temp_unit_user.update_or_insert((db.temp_unit_user.unit_id==unit_id) & (db.temp_unit_user.user_id==user_id)\
                                                       & (db.temp_unit_user.uuid==uid), unit_id=unit_id, user_id=user_id, uuid=uid,\
                                                       access_type=access,status="pending")
                    db.commit()
                    db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),change_available=1)
                    db.commit()
                else:
                    tmp_acc = db((db.temp_unit_user.unit_id==unit_id) & (db.temp_unit_user.user_id==user_id)).select(db.temp_unit_user.access_type)
                    if tmp_acc:
                        for acc in tmp_acc:
                            if access != acc.access_type:
                                db((db.temp_unit_user.unit_id==unit_id) & (db.temp_unit_user.user_id==user_id)).delete()
                                db.commit()
                                db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),change_available=0)
                                db.commit()
        elif access != 'No Access':
            db.temp_unit_user.update_or_insert((db.temp_unit_user.unit_id==unit_id) & (db.temp_unit_user.user_id==user_id) &\
                                               (db.temp_unit_user.uuid==uid),unit_id=unit_id,user_id=user_id,uuid=uid,access_type=access,status="pending")
            db.commit()
            db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),change_available=1)
            db.commit()
        i += 1
    redirect(URL('default', 'usermanagement'))
    return dict()
@auth.requires_login()
def addunit():
    if not auth.user_id:
        redirect(URL('login'))
    return dict()
@auth.requires_login()
def registerUnit():
    client_id= "%(client_id)s" % auth.user
    device_name=request.post_vars.devicename
    device_type=request.post_vars.devicetype
    unit = request.post_vars.unit
    if unit=='fingerprint':
        device_id = request.post_vars.deviceid
        model = request.post_vars.model
        vendor = request.post_vars.vendor
        query = db(db.Units.unit_id==device_id).select()
        if not query:
            db.Units.insert(unit_id=device_id, unit_name=device_name, dev_type=device_type, model=model, vendor=vendor)
            db.commit()
            db.Client_Unit.insert(client_id=client_id, unit_id=device_id)
            db.commit()
            db.control_instruction.insert(unit_id=device_id,update_flag=0, ulog_flag=2, uinfo_flag=2)
            db.commit()
            session.flash = "Your device added!"
            redirect(URL('default','addunit'))
        else:
            session.flash = "Device already registered!"
            redirect(URL('default','addunit'))
    elif unit=='rfid':
        device_id = request.post_vars.deviceid
        model = request.post_vars.model
        query = db(db.Units.unit_id==device_id).select()
        if not query:
            db.Units.insert(unit_id=device_id, unit_name=device_name, dev_type=device_type, model=model)
            db.commit()
            db.Client_Unit.insert(client_id=client_id, unit_id=device_id)
            db.commit()
            db.control_instruction.insert(unit_id=device_id,update_flag=0, ulog_flag=1, uinfo_flag=1)
            db.commit()
            session.flash = "Your device added!"
            redirect(URL('default','addunit'))
        else:
            response.flash = 'Device already registered!'
            redirect(URL('default','addunit'))
    elif unit=='mobile':
        client_id = "%(client_id)s" % auth.user
        longi = request.post_vars.longitude
        lati  = request.post_vars.latitude
        unit_id = client_id + str(float(lati)) + str(float(longi))
        query = db(db.Units.unit_id==unit_id).select()
        if not query:
            db.Units.insert(unit_id=unit_id,unit_name=device_name,latitude=lati,longitude=longi,dev_type=device_type)
            db.commit()
            db.Client_Unit.insert(client_id=client_id,unit_id=unit_id)
            db.commit()
            db.control_instruction.insert(unit_id=unit_id,new_unit=1,update_flag=0,ulog_flag=1,uinfo_flag=1)
            db.commit()
            session.flash = 'Your device added'
            redirect(URL('default','addunit'))
    return dict()
@auth.requires_login()
def userinfo():
    data = request.post_vars
    for d in data:
        uid = uuid.uuid1()
        client_id = db.Client_Unit(db.Client_Unit.unit_id==data['unit_id']).client_id
        query = db((db.Users.user_id==data['user_id']) & (db.Users.fingerprint_1 ==data['fp0'])).select()
        if not query:
            db.Users.insert(uuid=uid, user_id=data['user_id'], user_name=data['user_name'], fingerprint_1=data['fp0'],\
                            fingerprint_2=data['fp1'], password=data['password'], card=data['card'], privilege=data['privilege'])
            db.commit()
            db.Client_Unit_User.insert(client_id=client_id,unit_id=data['unit_id'],user_id=data['user_id'],uuid=uid)
            db.commit()
            db.Unit_Users.insert(uuid=uid, unit_id=data['unit_id'], user_id=data['user_id'], access_type='Regular Access')
            db.commit()
    return dict()

def get_all_user_info():
    response.headers['content-type'] = 'text/json'
    req = request.body.read()
    doc = json.loads(req)
    i=0
    while len(doc) > i:
        uid = uuid.uuid1()
        docs = doc[i]
        unit_id = str(docs['unit_id'])
        user_id = int(docs['user_id'])
        user_name = str(docs['user_name'])
        fp0 = docs['fp0']
        fp0_size = docs['fp0_size']
        fp1 = docs['fp1']
        fp1_size = docs['fp1_size']
        password = docs['password']
        card = docs['card']
        privilege = int(docs['privilege'])
        if user_id != 0:
            client_id = db.Client_Unit(db.Client_Unit.unit_id==unit_id).client_id
            in_client_user = db((db.Client_User.client_id==client_id) & (db.Client_User.user_id==user_id)).select()
            in_unit_user = db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).select()
            if not in_client_user:
                db.User_Info.insert(uuid=uid, user_id=user_id,user_name=user_name,fp0=fp0,fp0_size=fp0_size,\
                                    fp1=fp1,fp1_size=fp1_size,password=password,card=card)
                db.commit()
                db.Client_User.insert(client_id=client_id,user_id=user_id,uuid=uid)
                db.commit()
                if privilege==14:
                    db.Unit_Users.insert(uuid=uid,unit_id=unit_id, user_id=user_id,access_type="Admin")
                    db.commit()
                else:
                    db.Unit_Users.insert(uuid=uid,unit_id=unit_id, user_id=user_id,access_type="Regular Access")
                    db.commit()
                db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),update_flag=0,ulog_flag=1, uinfo_flag=1)
                db.commit()
            else:
                if not in_unit_user:
                    uniqueid = db.Client_User((db.Client_User.client_id==client_id) & (db.Client_User.user_id==user_id)).uuid
                    if privilege==14:
                        db.Unit_Users.insert(uuid=uniqueid,unit_id=unit_id,user_id=user_id,access_type="Admin")
                        db.commit()
                    else:
                        db.Unit_Users.insert(uuid=uniqueid,unit_id=unit_id,user_id=user_id,access_type="Regular Access")
                        db.commit()
                if privilege==14:
                    access_type=db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).select(db.Unit_Users.access_type)
                    for access in access_type:
                        if access.access_type=='Regular Access':
                            db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).update(access_type='Admin')
                            db.commit()
                else:
                    db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).update(access_type='Regular Access')
                    db.commit()
                db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),update_flag=0,ulog_flag=1, uinfo_flag=1)
                db.commit()
        i=i+1
    ret = dict()
    append_dic(ret,'result','success')
    return ret

def UserRegistration():
    if not auth.user:
        redirect(URL('login'))
    client_id= "%(client_id)s" % auth.user
    unit_id   = request.post_vars.unit
    first = str(request.post_vars.firstname)
    last  = str(request.post_vars.lastname)
    fullname  = first+' ' +last
    email     = request.post_vars.email
    father= request.post_vars.fathername
    mother= request.post_vars.mothername
    sess   = request.post_vars.session
    clsroll = request.post_vars.classroll
    card    = str(request.post_vars.card)
    phone     = request.post_vars.phone
    uid = uuid.uuid1()
    if type(unit_id) == list:
        for unit in unit_id:
            query = db((db.User_Info.user_id==card) & (db.User_Info.user_name==fullname)).select()
            if not query:
                db.User_Info.insert(uuid=uid,user_id=card,user_name=fullname,email=email,\
                                    fathers_name=father,mothers_name=mother,class_session=sess,classroll=clsroll,phone=phone)
                db.commit()
                db.Unit_Users.insert(unit_id=unit, user_id=card, uuid=uid, access_type="Regular Access")
                db.commit()
                db.Client_User.insert(client_id=client_id,user_id=card,uuid=uid)
                db.commit()
                row = db(db.control_instruction.unit_id == unit).select().first()
                row.update_record(uinfo_flag=1,new_user=1)
        session.flash = "User registered!"
        redirect(URL('default','UserRegistration'))
    elif type(unit_id) == str:
        query = db((db.User_Info.user_id==card) & (db.User_Info.user_name==fullname)).select()
        if not query:
            db.User_Info.insert(uuid=uid,user_id=card,user_name=fullname,email=email,\
                                fathers_name=father,mothers_name=mother,class_session=sess,classroll=clsroll,phone=phone)
            db.commit()
            db.Unit_Users.insert(unit_id=unit_id, user_id=card, uuid=uid, access_type="Regular Access")
            db.commit()
            db.Client_User.insert(client_id=client_id,user_id=card,uuid=uid)
            db.commit()
            row = db(db.control_instruction.unit_id == unit_id).select().first()
            row.update_record(uinfo_flag=1,new_user=1)
            session.flash = "User registered!"
            redirect(URL('default','UserRegistration'))
    elif type(unit_id) == None:
        response.flash = "Please select your device"
    return dict()

@auth.requires_login()
def all_unit_log():
    cid = "%(client_id)s" % auth.user
    if not request.vars.log:
        redirect(URL(vars={'log':1}))
    else:
        log = int(request.vars.log)
    start = (log-1) * 10
    end = log * 10
    query = db(db.Client_Unit.client_id==cid).select(db.Client_Unit.unit_id)
    return dict(query = query, start=start,end=end)

@auth.requires_login()
def unit_log():
    uid = request.args(0)
    cid = "%(client_id)s" % auth.user
    unit_name = db.Units(db.Units.unit_id==uid).unit_name
    dt = datetime.now(pytz.timezone('Asia/Dhaka')).date()
    logs = db((db.Users_Log.unit_id==uid) & (db.Users_Log.access_date==dt)).select()
    #logs = db(db.Users_Log.unit_id==uid).select()
    return dict(logs=logs, unit_id=uid, unit_name=unit_name)

def absent():
    if not auth.user:
        redirect(URL('login'))
    client_id="%(client_id)s" % auth.user
    client_user = db(db.Client_User.client_id==client_id).select()
    return dict(client_user=client_user)

def add_regular(a,user_id,uuid):
    append_dic(a,"add_regular",user_id)
    append_dic(a,"add_regular_name",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).user_name)
    append_dic(a,"add_regular_pass",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).password)
    append_dic(a,"add_regular_group",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).group_no)
    append_dic(a,"add_regular_f0",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp0)
    append_dic(a,"add_regular_f0_size",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp0_size)
    append_dic(a,"add_regular_f1",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp1)
    append_dic(a,"add_regular_f1_size",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp1_size)
    append_dic(a,"add_regular_card",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).card)
    append_dic(a,"add_regular_privilege",0)

def add_admin(a,user_id,uuid):
    append_dic(a,"add_admin",user_id)
    append_dic(a,"add_admin_name",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).user_name)
    append_dic(a,"add_admin_pass",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).password)
    append_dic(a,"add_admin_group",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).group_no)
    append_dic(a,"add_admin_f0",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp0)
    append_dic(a,"add_admin_f0_size",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp0_size)
    append_dic(a,"add_admin_f1",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp1)
    append_dic(a,"add_admin_f1_size",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).fp1_size)
    append_dic(a,"add_admin_card",db.User_Info((db.User_Info.user_id==user_id) & (db.User_Info.uuid==uuid)).card)
    append_dic(a,"add_admin_privilege",10)


def comp_table():
    unit_id = request.vars.unit_id
    a = dict()
    query = db(db.temp_unit_user.unit_id==unit_id).select()
    for q in query:
        if q.access_type == 'No Access':
            append_dic(a, "remove", q.user_id)
        elif q.access_type == 'Regular Access':
            add_regular(a, q.user_id, q.uuid)
        elif q.access_type == 'Admin':
            add_admin(a, q.user_id, q.uuid)
        else:
            append_dic(a, '', '')
    return a

def getinstruction():
    unit_id=request.vars.unit_id
    client_id=request.vars.client_id
    instruction = dict()
    dt = datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%Y-%m-%d %H:%M:%S")
    dt = dt.split()
    date = dt[0]
    time = dt[1]
    if unit_id:
        if db(db.Units.unit_id==unit_id).count()>0:
            rows = db(db.control_instruction.unit_id==unit_id).select()
            append_dic(instruction,"update_flag",db.control_instruction(db.control_instruction.unit_id==unit_id).update_flag)
            append_dic(instruction,"new_user",db.control_instruction(db.control_instruction.unit_id==unit_id).new_user)
            append_dic(instruction,"ulog_flag",db.control_instruction(db.control_instruction.unit_id==unit_id).ulog_flag)
            append_dic(instruction,"uinfo_flag",db.control_instruction(db.control_instruction.unit_id==unit_id).uinfo_flag)
            append_dic(instruction,"change_available",db.control_instruction(db.control_instruction.unit_id==unit_id).change_available)
            append_dic(instruction,"date",date)
            append_dic(instruction,"time",time)
            append_dic(instruction,"ulog_start_time",db.control_instruction(db.control_instruction.unit_id==unit_id).ulog_start_time)
            append_dic(instruction,"ulog_end_time",db.control_instruction(db.control_instruction.unit_id==unit_id).ulog_end_time)
    if client_id:
        units = db(db.Client_Unit.client_id==client_id).select()
        if units:
            for unit in units:
                newunit = db((db.control_instruction.unit_id==unit.unit_id) & (db.control_instruction.new_unit==1)).select()
                if newunit:
                    append_dic(instruction,"new_unit",db.control_instruction((db.control_instruction.unit_id==unit.unit_id)\
                                                                             & (db.control_instruction.new_unit==1)).new_unit)
    return instruction

def changeflag():
    x = request.vars.unit_id
    row = db(db.control_instruction.unit_id == x).select().first()
    row.update_record(new_unit=0,uinfo_flag=0)
    return dict()

def get_att_log():

    response.headers['content-type'] = 'text/json'
    req = request.body.read()
    array = json.loads(req)
    rows = array['Row']
    #db.Jsondata.insert(jsondata=array)
    #db.commit()

    for row in rows:
        if row == 'unit_id':
            continue
        else:
            unit_id = rows['unit_id']
            status = rows[row]['Status']
            workcode = rows[row]['WorkCode']
            verified = rows[row]['Verified']
            user_id  = rows[row]['PIN']
            date_time = rows[row]['DateTime']
            dt = date_time.split()
            d = dt[0]
            t = dt[1]
            is_in_unit_users = db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).select()
            if is_in_unit_users:
                #query = db((db.Users_Log.unit_id==unit_id) & (db.Users_Log.user_id == user_id) & (db.Users_Log.access_date==d) & (db.Users_Log.access_time==t)).select()
                #if not query:
                db.Users_Log.insert(unit_id=unit_id,user_id=user_id,access_date=d,access_time=t,verified=verified,status=status,workcode=workcode)
                db.commit()
                for user in is_in_unit_users:
                    db.Last_Attended.update_or_insert((db.Last_Attended.uuid==user.uuid), \
                                                      uuid=user.uuid,user_id=user_id,attend_date=d, attend_time=t)
                    db.commit()
                    db.control_instruction.update_or_insert(db.control_instruction.unit_id==unit_id, ulog_flag=1)
                    db.commit()
    ret = dict()
    append_dic(ret,'result','success')
    return ret
    #return dict()

def get_rfid_user_log():
    response.headers['content-type'] = 'text/json'
    req = request.body.read()
    db.Jsondata.insert(jsondata=req)
    data = json.loads(req)
    db.commit()
    i = 0
    while len(data['ID']) > i :
        user_id = data['ID'][i]
        date = data['date'][i]
        time = data['time'][i]
        db.Users_Log.insert(unit_id=unit_id, user_id=user_id, access_date=date, access_time=time)
        db.commit()
        i += 1
    return dict()

def client_user():
    client_id="%(client_id)s" % auth.user
    units = db(db.Client_Unit.client_id==client_id).select(db.Client_Unit.unit_id)
    for unit in units:
        users=db(db.Unit_Users.unit_id==unit.unit_id).select(db.Unit_Users.user_id)
        for id in users:
            user_id=id.user_id
            query = db((db.Client_User.client_id==client_id) & (db.Client_User.user_id==user_id)).select()
            if not query:
                db.Client_User.insert(client_id=client_id,user_id=user_id)
    return dict()


def registeredunit():
    unit_id = request.vars.unit_id
    query = db(db.Units.unit_id==unit_id).select()
    if query:
        result = "registered"
    else:
        result = "Not found"
    return dict(result=result)

def registereduser():
    user = dict()
    unit_id = request.vars.unit_id
    query = db(db.Unit_Users.unit_id==unit_id).select(db.Unit_Users.user_id)
    if query:
        for q in query:
            append_dic(user, "card_no", q.user_id)
    return user

def getSuccess():
    unit_id=request.vars.unit_id
    row = db(db.control_instruction.unit_id == unit_id).select().first()
    row.update_record(new_user=0)
    return dict()

def edited_users():
    unit_id = request.vars.unit_id
    query = db(db.temp_unit_user.unit_id==unit_id).select()
    for q in query:
        user_id=q.user_id
        access_type=q.access_type
        uid = q.uuid
        if access_type=='No Access':
            db((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id)).delete()
            db.commit()
        else:
            db.Unit_Users.update_or_insert((db.Unit_Users.unit_id==unit_id) & (db.Unit_Users.user_id==user_id),\
                                           unit_id=unit_id,user_id=user_id,uuid=uid,access_type=access_type)
            db.commit()

        db((db.temp_unit_user.unit_id==unit_id) & (db.temp_unit_user.user_id==user_id)).delete()
        db.commit()
        db.control_instruction.update_or_insert((db.control_instruction.unit_id==unit_id),change_available=0)
        db.commit()
    return dict()

def updateUser():
    id = request.args(0,cast=int)
    db.User_Info.uuid.readable=db.User_Info.uuid.writable=False
    db.User_Info.user_id.readable=db.User_Info.user_id.writable=False
    db.User_Info.fp0.readable=db.User_Info.fp0.writable=False
    db.User_Info.fp0_size.readable=db.User_Info.fp0_size.writable=False
    db.User_Info.fp1.readable=db.User_Info.fp1.writable=False
    db.User_Info.fp1_size.readable=db.User_Info.fp1_size.writable=False
    db.User_Info.face.readable=db.User_Info.face.writable=False
    db.User_Info.retina.readable=db.User_Info.retina.writable=False
    form=SQLFORM(db.User_Info,id,showid=False).process(next='usermanagement')
    return dict(form=form)

def isAlive():
    unit_id = request.vars.unit_id
    connected = request.vars.datetime
    server_datetime = datetime.now()
    is_unit_in_db = db(db.Units.unit_id==unit_id).select()
    if is_unit_in_db:
        client_id = db.Client_Unit(db.Client_Unit.unit_id==unit_id).client_id
        db.Alive.update_or_insert((db.Alive.client_id==client_id) & (db.Alive.unit_id==unit_id), client_id=client_id,\
                                  unit_id=unit_id,last_connected=connected,server_datetime=server_datetime)
        db.commit()
    return dict()

@auth.requires_login()
def deviceStatus():
    if not auth.user:
        redirect(URL('user/login'))
    client_id = "%(client_id)s" % auth.user
    units = db(db.Client_Unit.client_id==client_id).select()
    return dict(units=units)

def pendingStatus():
    client_id = "%(client_id)s" % auth.user
    ClientUnits = db(db.Client_Unit.client_id==client_id).select(db.Client_Unit.unit_id)
    st = ''
    for unit in ClientUnits:
        status = db(db.temp_unit_user.unit_id==unit.unit_id).select(db.temp_unit_user.status)
        if status:
            stat = 'Previous changes are pending'
            return stat
        else:
            st='Refresh if you want to see the recent changes.Database is synced with your device'
            return st

@auth.requires_login()
def leavemanagement():
    if not auth.user:
        redirect(URL('user/login'))
    client_id = "%(client_id)s" % auth.user
    client_user = db(db.Client_User.client_id==client_id).select()
    today = datetime.now().date()
    return dict(client_id=client_id, client_user=client_user)

def leave_granted():
    client_id="%(client_id)s" % auth.user
    data = request.post_vars
    if db.Variables(db.Variables.leave_id > 0):
        leave_id=db.Variables(db.Variables.leave_id > 0).leave_id
    else:
        db.Variables.update_or_insert(db.Variables.leave_id==None,leave_id=1)
        db.commit()
    if (data['startdate'] != '') & (data['enddate'] != ''):
        if (datetime.strptime(data['enddate'], '%Y-%m-%d').date() >= datetime.strptime(data['startdate'], '%Y-%m-%d').date()):
            user = data['user_id'].split(',')
            user_id=user[0]
            uuid=user[1]
            start_date = datetime.strptime(data['startdate'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['enddate'], '%Y-%m-%d').date()
            id=db.Variables(db.Variables.leave_id > 0).leave_id
            query = db((db.Leave_Granted.client_id==client_id) & (db.Leave_Granted.uuid==uuid) & (db.Leave_Granted.user_id==user_id) & \
                       (db.Leave_Granted.start_date==start_date) & (db.Leave_Granted.end_date==end_date)).select()
            if not query:
                db.Leave_Granted.insert(client_id=client_id,uuid=uuid,user_id=user_id,leave_id=id,start_date=start_date,end_date=end_date)
                db.commit()
                delta = end_date - start_date
                for i in range(delta.days + 1):
                    day = start_date + timedelta(days=i)
                    db.Leave_User.insert(client_id=client_id,uuid=uuid,user_id=user_id,leave_id=id,leave_date=day)
                    db.commit()
                db(db.Variables.leave_id > 0).update(leave_id=id+1)
                db.commit()
            session.flash = 'Data Inserted'
            redirect(URL('leavemanagement'))
        else:
            session.flash = 'End date must be greater'
            redirect(URL('leavemanagement'))
    else:
        session.flash = 'please select dates'
        redirect(URL('leavemanagement'))

    return dict()

def updateLeave():
    id = request.args(0,cast=int)
    db.Leave_Granted.uuid.readable=db.Leave_Granted.uuid.writable=False
    db.Leave_Granted.user_id.readable=db.Leave_Granted.user_id.writable=False
    db.Leave_Granted.user_name.readable=db.Leave_Granted.user_name.writable=False
    db.Leave_Granted.client_id.readable=db.Leave_Granted.client_id.writable=False
    form=SQLFORM(db.Leave_Granted,id,showid=False).process(next='leavemanagement')
    return dict(form=form)

def deleteLeave():
    client_id=request.args(0)
    user_id=request.args(1)
    uuid=request.args(2)
    leave_id=request.args(3,cast=int)
    db((db.Leave_Granted.leave_id==leave_id) & (db.Leave_Granted.client_id==client_id) & (db.Leave_Granted.user_id==user_id)).delete()
    db.commit()
    db((db.Leave_User.leave_id==leave_id) & (db.Leave_User.user_id==user_id) & (db.Leave_User.client_id==client_id)).delete()
    db.commit()
    redirect(URL('leavemanagement'))
    return dict()

@auth.requires_login()
def email():
    user_email = request.vars.mail
    if request.post_vars.submit:
        InputName = request.post_vars.InputName
        InputEmail = request.post_vars.InputEmail
        InputMessage = request.post_vars.InputMessage
        mail.send(to=[user_email,'kzubair.bd@gmail.com','enrhalim7@gmail.com'],
          subject='Contact From Name:{} and Email:{}'.format(InputName,InputEmail),
          # If reply_to is omitted, then mail.settings.sender is used
          reply_to=InputEmail,
          sender=InputEmail,
          message='Hi, {}'.format(InputMessage))
    return dict()

# For android app
def getUnits():
    client_id = request.vars.client_id
    units = db(db.Client_Unit.client_id==client_id).select(db.Client_Unit.unit_id)
    a = dict()
    for unit in units:
        append_dic(a, "Unit_Id", unit.unit_id)
        append_dic(a, "Unit_name",db.Units(db.Units.unit_id==unit.unit_id).unit_name)
        append_dic(a, "Latitude",db.Units(db.Units.unit_id==unit.unit_id).latitude)
        append_dic(a, "Longitude",db.Units(db.Units.unit_id==unit.unit_id).longitude)
    return a

def appUserRegistration():
    response.headers['content-type'] = 'application/json'
    data = json.loads(request.body.read())
    if len(data) > 0:
        fullname = data['fullname']
        mac_id = data['mac_id']
        client_id = data['employer_id']
        query = db(db.User_Info.user_id == mac_id).select()
        if query:
            #Mac ID already exists in the database
            status_flag = 0
            pass
        if not query:
            data = db(db.Client_Unit.client_id==client_id).select()
            if data:
                #Registration successful
                status_flag = 1
                uid = uuid.uuid1()
                # insert new user in the user_info table
                db.User_Info.insert(uuid = uid, user_id = mac_id, user_name = fullname)
                db.commit()
                # insert new user in the client_user table
                db.Client_User.insert(client_id=client_id,uuid=uid,user_id=mac_id)
                db.commit()
                for unit in data:
                    # insert new user in the unit_user table
                    db.Unit_Users.insert(unit_id=unit.unit_id,uuid=uid,user_id=mac_id)
                    db.commit()
            if not data:
                #Employer id doesn't exsit
                status_flag = 2
    return dict(status_flag=status_flag)

def appUserLog():
    response.headers['content-type'] = 'application/json'
    data = json.loads(request.body.read())
    if len(data) > 0:
        user_id=data['macid']
        client_id=data['empid']
        unit_id=data['unit_id']
        status = data['transition']
        date = data['date']
        time = data['time']
    return dict()

def get_month_dates(year, month, user_id):
    dates = []
    i = 1
    count = 0
    while i <= calendar.monthrange(year, month)[1]:
        dt = str(year) + '-' + str(month) + '-' + str(i)
        d = datetime.strptime(dt, "%Y-%m-%d").date()
        if d <= datetime.now().date():
            log = db((db.Users_Log.user_id==user_id) & (db.Users_Log.access_date==d)).select(db.Users_Log.access_time)
            if not log:
                count += 1
                dates.append(d.strftime("%Y-%m-%d"))
        i += 1
    return count, dates

@auth.requires_login()
def total_absent():
    if request.post_vars.submit:
        user_id=request.post_vars.user_id
        month = int(request.post_vars.month)
        year = datetime.now().year
        days = get_month_dates(year, month, user_id)
        return dict(days=days, month=month)
    return dict(days=0)

def absentCount():
    if db.Variables(db.Variables.absent_id > 0):
        absent_id=db.Variables(db.Variables.absent_id > 0).absent_id
    else:
        db.Variables.update_or_insert(db.Variables.absent_id==None,absent_id=1)
        db.commit()
    users = db(db.Client_User).select(db.Client_User.uuid,db.Client_User.user_id)
    for user in users:
        dt = datetime.now(pytz.timezone('Asia/Dhaka')).date()
        last_attend=db((db.Last_Attended.uuid==user.uuid) & (db.Last_Attended.attend_date==dt)).select().first()
        absent_count = db((db.Absent_Count.uuid==user.uuid) & (db.Absent_Count.absent_days==dt)).select().first()
        if (not last_attend) and (not absent_count):
            holiday = db(db.Holidays.holiday==dt).select(db.Holidays.holiday).first()
            leave = db((db.Leave_User.uuid==user.uuid) & (db.Leave_User.leave_date==dt)).select(db.Leave_User.user_id).first()
            if (not holiday) and (not leave):
                id=db.Variables(db.Variables.absent_id > 0).absent_id
                last_working_day_flag = 0
                temp_last_working_day = dt - timedelta(1)
                while (last_working_day_flag==0):
                    holiday = db(db.Holidays.holiday==temp_last_working_day).select(db.Holidays.holiday).first()
                    leave = db((db.Leave_User.uuid==user.uuid) &\
                               (db.Leave_User.leave_date==temp_last_working_day)).select(db.Leave_User.user_id).first()
                    if (not holiday) and (not leave):
                        last_working_day = temp_last_working_day
                        last_working_day_flag += 1
                        count = db((db.Absent_Count.uuid==user.uuid) & (db.Absent_Count.absent_days==last_working_day))\
                        .select(db.Absent_Count.consecutive_count,db.Absent_Count.absent_id).first()
                        if not count:
                            db.Absent_Count.insert(absent_id=id,uuid=user.uuid,user_id=user.user_id,absent_days=dt,consecutive_count=1)
                            db.commit()
                            db(db.Variables.absent_id > 0).update(absent_id=id+1)
                            db.commit()
                        else:
                            db.Absent_Count.insert(absent_id=count.absent_id,uuid=user.uuid,user_id=user.user_id,\
                                                   absent_days=dt,consecutive_count=count.consecutive_count+1)
                            db.commit()
                    else:
                        temp_last_working_day = temp_last_working_day - timedelta(1)
    return dict()

def absent_log():
    if request.post_vars.submit:
        start = request.post_vars.start
        end = request.post_vars.end
        client_id = "%(client_id)s" % auth.user
        client_user = db(db.Client_User.client_id==client_id).select(db.Client_User.uuid, db.Client_User.user_id)
        return dict(start=start,end=end,client_user=client_user)
    return dict(start=0,end=0,client_user=0)

def delete_unit():
    return locals()

def delete_user():
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
