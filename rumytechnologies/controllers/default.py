# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def index():
    return locals()

def about():
    return locals()

from gluon.tools import Mail
mail = auth.settings.mailer
mail.settings.server = 'localhost:25'
mail.settings.sender = 'admin@rumytechnologies.com'
mail.settings.login = None #'admin@rumytechnologies.com:RumyTech1@bd'
mail.settings.tls = True
mail.settings.ssl = False
def mailtous():
    name=request.vars['name']
    surname= request.vars['surname']
    email = request.vars['email']
    phone = ""
    phone = request.vars['phone']
    msg = request.vars['message']
    mail.send(to='arif_iftakher@rumy.io ',
              subject='Email received from Rumy Technology',
              reply_to= email,
              sender= email,
              message= "Name : "+ name + " " + surname + " \nEmail : " + email +"\nMessage : "+ msg + ".\n"
             )
    session.flash = 'Thank you, your email is sent!'
    redirect(URL('default','contact'))
    return locals()

def contact():
    return locals()

def product():
    return locals()

def career():
    return locals()

def expertise():
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

def product_rams():
    form = SQLFORM.factory(
    Field('email', requires =[ IS_EMAIL(error_message='invalid email!'), IS_NOT_EMPTY() ]),
    Field('message', requires=IS_NOT_EMPTY(), type='text')
    )
    if form.process().accepted:
        session.email = form.vars.email
        session.message = form.vars.message
        if mail:
            if mail.send(to=['arif_iftakher@rumy.io'],
                subject='Message recevied regarding RAMS',
                reply_to= session.email,
                sender= session.email,
                message= "Sender : "+ session.email+" \nMessage : "+session.message+ ".\n "
                        ):
                response.flash = 'Email sent sucessfully.'
            else:
                response.flash = 'Failed to send email, try again.'
            pass
        else:
            response.flash = 'Unable to send the email : email parameters not defined'
        pass
    elif form.errors:
            response.flash='Email form has errors.'
    pass
    return locals()


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
