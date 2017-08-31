# -*- coding: utf-8 -*-
from datetime import datetime

db.define_table('Clients',
                Field('client_id', 'string'),
                Field('name', 'string', requires=IS_NOT_EMPTY()),
                Field('email', 'string'),
                Field('phone', 'integer', requires=IS_NOT_EMPTY()),
                Field('address', 'string', requires=IS_NOT_EMPTY()),
                primarykey=['client_id'])

db.Clients.email.requires = [IS_NOT_EMPTY(), IS_EMAIL()]

db.define_table('Units',
                Field('unit_id', 'string'),
                Field('unit_name', 'string'),
                Field('dev_type', 'string'),
                Field('model', 'string'),
                Field('vendor', 'string'),
                Field('latitude','string'),
                Field('longitude','string'),
                Field('template_capacity', 'integer'),
                Field('login_capacity', 'integer'),
                primarykey=['unit_id'],migrate=True, fake_migrate=True)

db.define_table('control_instruction',
                Field('unit_id'),
                Field('new_unit'),
                Field('new_user'),
                Field('update_flag'),
                Field('ulog_flag'),
                Field('uinfo_flag'),
                Field('change_available'),
                Field('ulog_start_time', 'datetime'),
                Field('ulog_end_time', 'datetime'),migrate=True, fake_migrate=True)



db.define_table('User_Info',
                Field('uuid','string'),
                Field('user_id', 'string'),
                Field('user_name', 'string', requires=IS_NOT_EMPTY()),
                Field('department', 'string'),
                Field('fp0', 'text', requires=IS_NOT_EMPTY()),
                Field('fp0_size', 'integer'),
                Field('fp1', 'text', requires=IS_NOT_EMPTY()),
                Field('fp1_size'),
                Field('face','string'),
                Field('retina','string'),
                Field('password', 'string'),
                Field('group_no'),
                Field('card', 'string'),
                Field('phone'),
                Field('email'),
                Field('fathers_name'),
                Field('mothers_name'),
                Field('address'),
                Field('class_session'),
                Field('classroll'),
                Field('privilege', 'integer'), migrate=True, fake_migrate=True)

db.define_table('Client_Unit',
                Field('client_id'),
                Field('unit_id'))

db.define_table('Unit_Users',
                Field('unit_id', 'string'),
                Field('user_id', 'string'),
                Field('uuid', 'string'),
                Field('access_type', 'string'),migrate=True, fake_migrate=True)

db.define_table('Client_User',
                Field('client_id','string'),
                Field('user_id','string'),
                Field('uuid','string'),migrate=True, fake_migrate=True)

db.define_table('Client_Unit_User',
                Field('client_id', 'string'),
                Field('unit_id','string'),
                Field('user_id', 'string'),
                Field('uuid', 'string'),migrate=True, fake_migrate=True)

db.define_table('test',
                Field('user_id', 'string'),
                Field('user_name', 'string'),
                Field('password', 'string'),
                Field('card', 'string'),migrate=True, fake_migrate=True)

db.define_table('Access_Type',
                Field('id', 'integer'),
                Field('access_type', 'string'),
                primarykey=['id'],migrate=True, fake_migrate=True)

db.define_table('Accesses',
                Field('id', 'integer'),
                Field('access_type', 'string'),
                primarykey=['id'],migrate=True, fake_migrate=True)

db.define_table('temp_unit_user',
                Field('unit_id', 'string'),
                Field('user_id', 'string'),
                Field('uuid', 'string'),
                Field('access_type', 'string'),
                Field('status', 'string'),migrate=True, fake_migrate=True)

db.define_table('Users_Log',
                Field('unit_id', 'string'),
                Field('user_id', 'string'),
                Field('access_date', 'string'),
                Field('access_time', 'string'),
                Field('verified'),
                Field('status'),
                Field('workcode'),migrate=True, fake_migrate=True)


db.define_table('Last_Attended',
               Field('uuid', 'string'),
               Field('user_id'),
               Field('attend_date', 'date'),
               Field('attend_time', 'time'),migrate=True, fake_migrate=True)

db.define_table('Alive',
                Field('client_id'),
                Field('unit_id'),
                Field('last_connected','datetime'),
                Field('server_datetime','datetime'),migrate=True, fake_migrate=True)

db.define_table('Leave_Granted',
                Field('client_id'),
                Field('uuid'),
                Field('user_id'),
                Field('leave_id'),
                Field('start_date', 'date'),
                Field('end_date', 'date'),migrate=True, fake_migrate=True)

db.define_table('Leave_User',
                Field('client_id'),
                Field('uuid'),
                Field('user_id'),
                Field('leave_id'),
                Field('leave_date', 'date'),migrate=True, fake_migrate=True)


db.define_table('Jsondata',
               Field('jsondata'),
               Field('privilege'))

db.define_table('Holidays',
                Field('holiday','date'))

db.define_table('Variables',
                Field('leave_id', 'integer', default=1),
                Field('absent_id', 'integer', default=1))

db.define_table('Absent_Count',
                Field('absent_id'),
                Field('uuid','string'),
                Field('user_id','string'),
                Field('absent_days', 'date'),
                Field('consecutive_count','integer'))

db.define_table('cron_job',
                Field('request_date'),
                Field('request_time'))

"""
db.Variables.truncate()
db.Absent_Count.truncate()
db.Leave_Granted.truncate()
db.Leave_User.truncate()
db.Users_Log.truncate()
db.Last_Attended.truncate()

"""
"""
db.Units.truncate()
db.Client_Unit.truncate()

db.User_Info.truncate()
db.Unit_Users.truncate()
db.Client_User.truncate()
db.control_instruction.truncate()
db.Client_Unit_User.truncate()
db.temp_unit_user.truncate()
db.Alive.truncate()
db.Last_Attended.truncate()
db.Users_Log.truncate()
db.Absent_Count.truncate()
db.Variables.truncate()
db.Absent_Count.truncate()
db.Leave_Granted.truncate()
db.Leave_User.truncate()
"""
