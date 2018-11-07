# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as django_auth_views
from django.contrib import messages
from django import http as django_http
from django import shortcuts
from django.utils import functional
from django.utils import http
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from keystoneauth1 import exceptions as keystone_exceptions
import six

from openstack_auth import exceptions
from openstack_auth import forms
from openstack_auth import plugin

# This is historic and is added back in to not break older versions of
# Horizon, fix to Horizon to remove this requirement was committed in
# Juno
from openstack_auth.forms import Login  # noqa:F401
from openstack_auth import user as auth_user
from openstack_auth import utils

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
#from kolla_docker.zun.zun.db.sqlalchemy.models import User
import sys
#sys.path.insert(0, '/root/kolla-docker/zun/zun/db/sqlalchemy/')
#sys.path.insert(0, '/root/kolla-docker/zun-ui/zun_ui/api/rest_api_user')
sys.path.append('../')
sys.path.append('../../')
from zunclient.v1 import client as zun_client
#from zun.objects import user
from zun_ui.api import rest_api
#from zun.db.sqlalchemy import models
from django.contrib.auth import login, authenticate

#from openstack_auth.forms import SignUpForm


#from django.contrib.auth import get_user_model
#User = get_user_model()

from django.http import HttpResponseRedirect
from .forms import PassResetForm, NewPassForm, UserLoginForm, UserSignupForm#, SignUpForm

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import datetime
from datetime import datetime
from datetime import timedelta
from django.utils import timezone

import re
import pytz
from oslo_utils import timeutils
import urllib2
from django.test.client import RequestFactory

try:
    is_safe_url = http.is_safe_url
except AttributeError:
    is_safe_url = utils.is_safe_url


LOG = logging.getLogger(__name__)


def _cleanup_params(attrs, check, **params):
    args = {}
    run = False

    for (key, value) in params.items():
        if key == "run":
            run = value
        elif key == "cpu":
            args[key] = float(value)
        elif key == "memory":
            args[key] = int(value)
        elif key == "interactive" or key == "nets" \
                or key == "security_groups" or key == "hints":
            args[key] = value
        elif key == "restart_policy":
            args[key] = utils.check_restart_policy(value)
        elif key == "environment" or key == "labels":
            values = {}
            vals = value.split(",")
            for v in vals:
                kv = v.split("=", 1)
                values[kv[0]] = kv[1]
            args[str(key)] = values
        elif key in attrs:
            if value is None:
                value = ''
            args[str(key)] = str(value)
        elif check:
            LOG.debug('zunclient xxx exception %s xxx' % key)
            raise exceptions.BadRequest(
                "Key must be in %s" % ",".join(attrs))

    return args, run

def _cleanup_user_params(attrs, check, **params):
    args = {}
    run = False

    for (key, value) in params.items():
        if key == "run":
            run = value
        elif key == "cpu":
            args[key] = float(value)
        elif key == "memory":
            args[key] = int(value)
        elif key == "interactive" or key == "nets" \
                or key == "security_groups" or key == "hints":
            args[key] = value
        elif key == "restart_policy":
            args[key] = utils.check_restart_policy(value)
        elif key == "environment" or key == "labels":
            values = {}
            vals = value.split(",")
            for v in vals:
                kv = v.split("=", 1)
                values[kv[0]] = kv[1]
            args[str(key)] = values
        elif key in attrs:
            if value is None:
                value = ''
            args[str(key)] = str(value)
        elif check:
            LOG.debug('zunclient xxx exception %s xxx' % key)
            raise exceptions.BadRequest(
                "Key must be in %s" % ",".join(attrs))

    return args, run

CREATION_ATTRIBUTES = ['id', 'user_name', 'last_name', 'first_name', 'middle_name', 'password', 'uuid',
                       'account_status', 'failed_attempt', 'last_login_method', 'current_user_charge_tier', 'admin_ind',
                       'displayname', 'passreset_url', 'activation_url', 'activation_expir_date', 'passreset_expir_date',
                       'last_login_time', 'last_success_login_ip', 'last_failed_login_ip',

                       'name', 'image', 'command', 'cpu', 'memory',
                       'environment', 'workdir', 'labels', 'image_pull_policy',
                       'restart_policy', 'interactive', 'image_driver',
                       'security_groups', 'hints', 'nets', 'auto_remove'
                                                           'carrier', 'carrier_name', 'carrier_access_key',
                       'carrier_access_key_id']

USER_CREATE_ATTRS = CREATION_ATTRIBUTES


def get_user_id(userinfo_keystone, user_name):
    for user in userinfo_keystone:
        if user.name == user_name:
            return user.id

    '''sub = str(userinfo_keystone).split(",")
    for j in range(0, len(sub)):
        if sub[j].find(" id=") != -1:
            id = sub[j].split("=")
            return id[1]'''

def get_project_id(projectinfo, project_name):
    for project in projectinfo:
        if project.name == project_name:
            return project.id

    '''for i in projectinfo:
        if str(i).find("name=" + project) != -1:
            sub = str(i).split(",")
            for j in range(0, len(sub)):
                if sub[j].find(" id=") != -1:
                    id = sub[j].split("=")
                    return id[1]'''

def get_role_id(roleinfo, role_name):
    for role in roleinfo:
        if role.name == role_name:
            return role.id

    '''for i in roleinfo:
        if str(i).find("name=" + role) != -1:
            sub = str(i).split(",")
            for j in range(0, len(sub)):
                if sub[j].find(" id=") != -1:
                    id = sub[j].split("=")
                    return id[1]'''

def get_zun_user_uuid(create_response):
    sub = str(create_response).split(",")
    for j in range(0, len(sub)):
        if sub[j].find("uuid") != -1:
            uuid = sub[j].split(": ")
            result = uuid[1].split("'")
            return result[1]

def get_list_user_uuid(get_user, user_name):
    for user in get_user:
        if user.user_name == user_name:
            return user.uuid


#take user password reset information and update the password in both zun user database and keystone user database
def pwr(request, uidb64, token, template_name=None, extra_context=None, **kwargs):
    if request.method == 'POST':
        form = NewPassForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            new_password_confirm = form.cleaned_data.get('new_password_confirm')

            if new_password != new_password_confirm:
                forbid_reset = "New password and new password confirm is not the same!"
                login_url = '/auth/pwr/' + uidb64 + '/' + token

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('newpass_failed_reason', forbid_reset, max_age=10)
                res.set_cookie('newpass_failed_status', "inconfirm password", max_age=10)
                return res

                #form = NewPassForm()
                #return render(request, 'newpassword.html', {'form': form, 'uid': uidb64, 'token': token})

            if not re.match(r"^(?=.*[a-zA-Z])(?=.*[0-9])", new_password) or len(new_password) < 5 or len(new_password) > 15:
                forbid_reset = "Invalid password format. Password must contain at least 1 letter and 1 numeric number, without space," \
                                " and the password length must between 5 and 15."
                login_url = '/auth/pwr/' + uidb64 + '/' + token

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('newpass_failed_reason', forbid_reset, max_age=10)
                res.set_cookie('newpass_failed_status', "invalid password", max_age=10)
                return res

            c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                  password="password", project_domain_id="default", project_domain_name="Default",
                                  project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                  user_domain_id="default",
                                  user_domain_name="Default", username="zun", region_name="RegionOne",
                                  service_name="zun",
                                  service_type="container")

            uid = force_text(urlsafe_base64_decode(uidb64))
            userinfo = c.users.get(uid)

            user_name = userinfo.user_name
            #LOG.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            #LOG.info(uid)
            #LOG.info(userinfo)
            #LOG.info(user_name)

            # zun database user update for password
            user_update_info_zun = {'password': new_password, 'failed_attempt': 0}

            args2, run2 = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

            c.users.update(uid, **args2)
            #LOG.info("xxxxxx signup update response xxxxxx")
            #LOG.info(update_response)

            #keystone database user update for password
            auth = v3.Password(auth_url="http://keystone.nova.svc.cluster.local:80/v3", username="admin",
                               password="password", project_name="admin", user_domain_id="default",
                               project_domain_id="default")

            sess = session.Session(auth=auth)
            keystone = client.Client(session=sess)
            userinfo_keystone = keystone.users.list(name=user_name)

            keystone_user_id = get_user_id(userinfo_keystone, user_name)
            #keystone_user_id = userinfo_keystone.id
            keystone.users.update(keystone_user_id, password = new_password)
            #LOG.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            #LOG.info(update_response)

            return shortcuts.render(request, 'passreset_to_login.html')
    else:
        form = NewPassForm()
        #uid = uidb64

    return render(request, 'newpassword/login.html', {'form': form, 'uid': uidb64, 'token': token})


#use to trigger the password reset page if the passreset_url in user's email is the same as the passreset_url in zun database
def passreset(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                              password="password", project_domain_id="default", project_domain_name="Default",
                              project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                              user_domain_id="default",
                              user_domain_name="Default", username="zun", region_name="RegionOne",
                              service_name="zun",
                              service_type="container")

        userinfo = c.users.get(uid)

        #LOG.info("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR c.user.get(uid) = RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        #LOG.info(userinfo)
        #LOG.info(request)
        #LOG.info(userinfo.passreset_url)

        current_site = get_current_site(request)

        link = render_to_string('password_link.html', {
            'domain': current_site.domain,
            # 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'uid': uidb64,
            'token': token,
        })

    except Exception:
        userinfo = None

    if userinfo is not None and link == userinfo.passreset_url:
        #return HttpResponseRedirect('/auth/pwr/' + uidb64)
        return redirect('/auth/pwr/' + uidb64 + '/' + token)
    else:
        return shortcuts.render(request, 'invalid_link.html')

#use to send password reset link to user's email box
def passwordreset(request, template_name=None, extra_context=None, **kwargs):
    if request.method == 'POST':
        form = PassResetForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('email')

            c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                  password="password", project_domain_id="default", project_domain_name="Default",
                                  project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                  user_domain_id="default",
                                  user_domain_name="Default", username="zun", region_name="RegionOne",
                                  service_name="zun",
                                  service_type="container")

            get_user = c.users.list(None, None, None, None)
            #LOG.info("passwordreset passwordreset passwordreset passwordreset passwordreset passwordreset passwordreset passwordreset passwordreset")
            #LOG.info(get_user)

            uuid = get_list_user_uuid(get_user, user_name)
            #LOG.info(uuid)

            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_name):
                forbid_passreset = "Please type username in valid email format."
                login_url = "/auth/passwordreset/"

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('passreset_failed_reason', forbid_passreset, max_age=10)
                res.set_cookie('passreset_failed_status', "invalid username", max_age=10)
                return res

            if uuid is None:
                #form = PassResetForm()
                #return render(request, 'passwordreset.html', {'form': form})
                not_exist = "User " + user_name + " does not exist. Please register!"

                login_url = "/auth/passwordreset/"

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('passreset_failed_reason', not_exist, max_age=10)
                res.set_cookie('passreset_failed_status', "not exist", max_age=10)

                return res

            else:
                userinfo = c.users.get(uuid)
                if userinfo.account_status == 1:

                    activate_first = "Please check your email to activate your login account first."

                    login_url = "/auth/passwordreset/"

                    res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                    res.set_cookie('passreset_failed_reason', activate_first, max_age=10)
                    res.set_cookie('passreset_failed_status', "not activate", max_age=10)

                    return res

            # send password reset email
            user = form.save(commit=False)
            user.is_active = False
            # user.save()
            current_site = get_current_site(request)
            #LOG.info(current_site)
            mail_subject = 'Reset your cloud account password.'

            fromaddr = "eternovainc0@gmail.com"
            toaddr = user_name
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = mail_subject

            token = account_activation_token.make_token(user)

            body = render_to_string('acc_passreset_email.html', {
                'user': user,
                'domain': current_site.domain,
                #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'uid': urlsafe_base64_encode(force_bytes(uuid)),
                'token': token,
            })

            link = render_to_string('password_link.html', {
                'user': user,
                'domain': current_site.domain,
                #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'uid': urlsafe_base64_encode(force_bytes(uuid)),
                'token': token,
            })

            passreset_url = link

            # zun database user update for passreset_url and passreset_expir_date
            passreset_expir_date = datetime.now() + timedelta(days=7)

            user_update_info_zun = {'passreset_url': passreset_url, 'passreset_expir_date': passreset_expir_date}

            args2, run2 = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

            c.users.update(uuid, **args2)
            #LOG.info("xxxxxx signup update response xxxxxx")
            #LOG.info(update_response)

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "nova:456")

            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()

            return shortcuts.render(request, 'passreset_confirm_email.html')
    else:
        form = PassResetForm()

    return render(request, 'passreset/login.html', {'form': form})

#use to activate the user account if the activation_url in user's email is the same as the activation_url in zun database
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                              password="password", project_domain_id="default", project_domain_name="Default",
                              project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                              user_domain_id="default",
                              user_domain_name="Default", username="zun", region_name="RegionOne",
                              service_name="zun",
                              service_type="container")

        userinfo = c.users.get(uid)

        #LOG.info("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR c.user.get(uid) = RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        #LOG.info(userinfo)
        #LOG.info(request)
        #LOG.info(userinfo.activation_url)

        current_site = get_current_site(request)

        link = render_to_string('email_link.html', {
            'domain': current_site.domain,
            # 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'uid': uidb64,
            'token': token,
        })


        #user = User.objects.get(pk=uid)
    #except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        #user = None
    except Exception:
        userinfo = None

    if userinfo is not None and link == userinfo.activation_url:
        user_name = userinfo.user_name
        password = userinfo.password
        uuid = userinfo.uuid
        #displayname = userinfo.displayname
        #userinfo_zun = {'user_name': user_name, 'password': password}

        #grant the user account to access to the openstack dashboard
        auth = v3.Password(auth_url="http://keystone.nova.svc.cluster.local:80/v3", username="admin",
                               password="password", project_name="admin", user_domain_id="default",
                               project_domain_id="default")

        #LOG.info("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        #LOG.info(auth)

        sess = session.Session(auth=auth)

        #LOG.info(sess)

        keystone = client.Client(session=sess)

        domain = "default"
        project_description = "Guest Project"

        project_name = re.sub(r'[^a-zA-Z0-9-]', "-", user_name)

        role_name = "admin"
        enabled = True
        user_description = "Guest User"

        userinfo_keystone = keystone.users.list(name=user_name)
        #LOG.info("optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization")
        user_id = get_user_id(userinfo_keystone, user_name)

        projectinfo = keystone.projects.list()
        project_id = get_project_id(projectinfo, project_name)

        roleinfo = keystone.roles.list()
        role_id = get_role_id(roleinfo, role_name)

        if project_id is None:
            keystone.projects.create(name=project_name, domain=domain, description=project_description, enabled=enabled)
            projectinfo = keystone.projects.list()
            project_id = get_project_id(projectinfo, project_name)

        if user_id is None:
            keystone.users.create(name=user_name, password=password, email=user_name, description=user_description,
                                domain=domain, enabled=enabled, project=project_name, role=role_name)
            userinfo_keystone = keystone.users.list(name=user_name)
            #LOG.info("optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization")
            user_id = get_user_id(userinfo_keystone, user_name)

        keystone.users.update(user_id, enabled=enabled)

        keystone.roles.grant(role=role_id, user=user_id, project=project_id)

        user_update_info_zun = {'account_status': 0}

        args, run = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

        c.users.update(uuid, **args)

        #LOG.info("xxxxxx signup update response xxxxxx")
        #LOG.info(update_response)

        return shortcuts.render(request, 'ready_to_login.html')
    else:
        return shortcuts.render(request, 'invalid_link.html')


#take user signup information and create a row of user information in zun user database
def signup(request, template_name=None, extra_context=None, **kwargs):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            #displayname = form.cleaned_data.get('displayname')

            #LOG.info("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
            #LOG.info(user_name)
            #LOG.info(password)
            #LOG.info(displayname)

            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_name):
                forbid_signup = "Please type username in valid email format."
                login_url = "/auth/signup/"

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('signup_failed_reason', forbid_signup, max_age=10)
                res.set_cookie('signup_failed_status', "invalid username", max_age=10)
                return res

            if not re.match(r"^(?=.*[a-zA-Z])(?=.*[0-9])", password) or len(password) < 5 or len(password) > 15:
                forbid_signup = "Password must contain at least 1 letter, at least 1 number, without other characters," \
                                " and be more than 5 characters and less than 15 characters."
                login_url = "/auth/signup/"

                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                res.set_cookie('signup_failed_reason', forbid_signup, max_age=10)
                res.set_cookie('signup_failed_status', "invalid password", max_age=10)
                return res




            c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                  password="password", project_domain_id="default", project_domain_name="Default",
                                  project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                  user_domain_id="default",
                                  user_domain_name="Default", username="zun", region_name="RegionOne",
                                  service_name="zun",
                                  service_type="container")

            get_user = c.users.list(None, None, None, None)
            uuid = get_list_user_uuid(get_user, user_name)

            if uuid is None:
                # create user in keystone and zun in the same time with the same uuid
                auth = v3.Password(auth_url="http://keystone.nova.svc.cluster.local:80/v3", username="admin",
                                   password="password", project_name="admin", user_domain_id="default",
                                   project_domain_id="default")

                sess = session.Session(auth=auth)

                keystone = client.Client(session=sess)

                domain = "default"
                #project_description = "Guest Project"

                project_name = re.sub(r'[^a-zA-Z0-9-]', "-", user_name)

                role_name = "admin"
                #enabled = False
                user_description = "Guest User"

                userinfo_keystone = keystone.users.list(name=user_name)
                # LOG.info("optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization")
                user_id = get_user_id(userinfo_keystone, user_name)

                #projectinfo = keystone.projects.list()
                #project_id = get_project_id(projectinfo, project_name)

                #roleinfo = keystone.roles.list()
                #role_id = get_role_id(roleinfo, role_name)

                '''if project_id is None:
                    keystone.projects.create(name=project_name, domain=domain, description=project_description,
                                             enabled=True)
                    projectinfo = keystone.projects.list()
                    project_id = get_project_id(projectinfo, project_name)'''

                if user_id is None:
                    keystone.users.create(name=user_name, password=password, email=user_name,
                                          description=user_description,
                                          domain=domain, enabled=False, project=project_name, role=role_name)
                    userinfo_keystone = keystone.users.list(name=user_name)
                    # LOG.info("optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization-optimization")
                    user_id = get_user_id(userinfo_keystone, user_name)

                #keystone.roles.grant(role=role_id, user=user_id, project=project_id)

                # zun database user create
                user_create_info_zun = {'user_name': user_name, 'password': password, 'account_status': 1,
                                        'failed_attempt': 0, 'uuid': user_id, 'displayname': user_name}

                args, run = _cleanup_params(USER_CREATE_ATTRS, True, **user_create_info_zun)

                create_response = c.users.create(**args)
                #LOG.info("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
                #LOG.info("xxxxxx signup create response xxxxxx")
                #LOG.info(create_response)

                uuid = get_zun_user_uuid(create_response)

            else:
                userinfo = c.users.get(uuid)
                if userinfo.account_status == 0:
                    forbid_signup = "User " + user_name + " exists! Please register with different username!"
                    login_url = "/auth/signup/"

                    res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                    res.set_cookie('signup_failed_reason', forbid_signup, max_age=10)
                    res.set_cookie('signup_failed_status', "user exist", max_age=10)
                    return res

            #send activation email
            user = form.save(commit=False)
            user.is_active = False
            #user.save()
            current_site = get_current_site(request)
            #LOG.info(current_site)
            mail_subject = 'Activate your cloud account.'

            fromaddr = "eternovainc0@gmail.com"
            toaddr = user_name
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = mail_subject

            token = account_activation_token.make_token(user)

            body = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'uid': urlsafe_base64_encode(force_bytes(uuid)),
                'token': token,
            })

            link = render_to_string('email_link.html', {
                'user': user,
                'domain': current_site.domain,
                #'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'uid': urlsafe_base64_encode(force_bytes(uuid)),
                'token': token,
            })

            activation_url = link


            #zun database user update for activation_url and activation_expir_date
            activation_expir_date = datetime.now() + timedelta(days=7)

            user_update_info_zun = {'password': password, 'activation_url': activation_url, 'activation_expir_date': activation_expir_date}

            args2, run2 = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

            c.users.update(uuid, **args2)
            #LOG.info("xxxxxx signup update response xxxxxx")
            #LOG.info(update_response)

            msg.attach(MIMEText(body, 'plain'))


            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "nova:456")

            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()

            '''signup = {'username': user_name}

            context = {
                'signup': signup,
            }'''

            #return render(request, 'auth/login.html', context)
            #return shortcuts.redirect('/auth/login/', context)
            return render(request, 'signup_confirm_email.html')
            #return HttpResponseRedirect('/index/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserSignupForm()

    return render(request, 'regist/login.html', {'form': form})

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name=None, extra_context=None, **kwargs):

    #LOG.info("come in to the login function!v2")
    #LOG.info(request.user.username)
    #if request.method == "POST":
        #LOG.info("uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
        #LOG.info(request.user.username)

    """Logs a user in using the :class:`~openstack_auth.forms.Login` form."""

    # If the user enabled websso and selects default protocol
    # from the dropdown, We need to redirect user to the websso url
    if request.method == 'POST':
        auth_type = request.POST.get('auth_type', 'credentials')
        #LOG.info("11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
        #LOG.info(request)
        #LOG.info(auth_type)

        if utils.is_websso_enabled() and auth_type != 'credentials':
            #LOG.info("22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222")

            auth_url = request.POST.get('region')

            #LOG.info(auth_url)
            url = utils.get_websso_url(request, auth_url, auth_type)

            #LOG.info(url)
            return shortcuts.redirect(url)

    if not request.is_ajax():
        # If the user is already authenticated, redirect them to the
        # dashboard straight away, unless the 'next' parameter is set as it
        # usually indicates requesting access to a page that requires different
        # permissions.
        if (request.user.is_authenticated() and
                auth.REDIRECT_FIELD_NAME not in request.GET and
                auth.REDIRECT_FIELD_NAME not in request.POST):
            return shortcuts.redirect(settings.LOGIN_REDIRECT_URL)

    # Get our initial region for the form.
    initial = {}
    current_region = request.session.get('region_endpoint', None)
    requested_region = request.GET.get('region', None)
    regions = dict(getattr(settings, "AVAILABLE_REGIONS", []))
    if requested_region in regions and requested_region != current_region:
        initial.update({'region': requested_region})

    if request.method == "POST":
        form = functional.curry(forms.Login)
    else:
        form = functional.curry(forms.Login, initial=initial)

    if extra_context is None:
        extra_context = {'redirect_field_name': auth.REDIRECT_FIELD_NAME}

    extra_context['csrf_failure'] = request.GET.get('csrf_failure')

    if not template_name:
        if request.is_ajax():
            template_name = 'auth/_login.html'
            extra_context['hide'] = True
        else:
            template_name = 'auth/login.html'

    #LOG.info("3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333")
    #LOG.info(forms.Login)
    #LOG.info(request)
    #LOG.info(request.user.username)
    #LOG.info(template_name)
    #LOG.info(form)
    #LOG.info(form.username)
    #LOG.info(extra_context)
    #LOG.info(kwargs)
    #LOG.info("before res = django_auth_views.login()")

    # check whether user attempt to login too often
    if request.method == "POST":
        form_login_attempt = UserLoginForm(request.POST)
        if form_login_attempt.is_valid():
            username = form_login_attempt.cleaned_data.get('username')
            #LOG.info(username)

            if username == "zun" or username == "admin":
                LOG.info("zun")

            #if username == "admin":
                #LOG.info(request.META)
                '''ipList = ["10.128.0.2", "10.233.66.1"]
                if request.META["REMOTE_ADDR"] not in ipList:
                    invalid_ip = "Invalid ip address: " + request.META["REMOTE_ADDR"] + " for admin login"
                    login_url = "/auth/login/"

                    res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                    res.set_cookie('login_failed_reason', invalid_ip, max_age=10)
                    res.set_cookie('login_failed_status', "invalid ip", max_age=10)
                    return res'''


            else:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
                    forbid_login = "Please type email in valid format."
                    login_url = "/auth/login/"

                    #LOG.info(forbid_login)

                    res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                    res.set_cookie('login_failed_reason', forbid_login, max_age=10)
                    res.set_cookie('login_failed_status', "invalid username", max_age=10)
                    return res

                c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                      password="password", project_domain_id="default", project_domain_name="Default",
                                      project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                      user_domain_id="default",
                                      user_domain_name="Default", username="zun", region_name="RegionOne",
                                      service_name="zun",
                                      service_type="container")
                get_user = c.users.list(None, None, None, None)
                uuid = get_list_user_uuid(get_user, username)
                if uuid is not None:
                    # this is the previous status of user in database, not the current status!
                    userinfo = c.users.get(uuid)

                    # this means the account has already been activated by email link
                    if userinfo.account_status == 0:
                        # update last_login_time as long as users tried to login
                        last_login_time = datetime.now()
                        user_update_info_zun = {'last_login_time': last_login_time}

                        args, run = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

                        c.users.update(uuid, **args)
                        #LOG.info("xxxxxx signup update response xxxxxx")
                        #LOG.info(update_response)

                        # check whether user attempt to login too often
                        if userinfo.last_login_time is not None:
                            naive_userinfo = userinfo.last_login_time.split("+")[0]
                            naive_userinfo = datetime.strptime(naive_userinfo, "%Y-%m-%d %H:%M:%S")

                            time_difference = last_login_time - naive_userinfo
                            #LOG.info("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

                            #LOG.info(time_difference)

                            time_interval = 4 ** userinfo.failed_attempt
                            if time_difference.seconds <= time_interval:
                                forbid_login = "Login blocked because of multiple failed logins. You can try again in " \
                                               + str(time_interval) + " seconds! Or RESET your password!"

                                '''login = {'forbid_login': forbid_login}
                                context = {
                                    'login': login,
                                }'''

                                # form = functional.curry(forms.Login, initial=initial)
                                # request.session.flush()

                                login_url = "/auth/login/"

                                res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                                res.set_cookie('login_failed_reason', forbid_login, max_age=10)
                                res.set_cookie('login_failed_status', "too often", max_age=10)
                                # rf = RequestFactory()
                                # get_request = rf.get('/auth/login/')
                                # post_request = rf.post('/auth/login/', {'username': username + "!"})
                                # request.user.username = username + "!"

                                # request.POST = request.POST.copy()
                                # request.POST["password"] = "_"

                                '''res = django_auth_views.login(request,
                                                              template_name=template_name,
                                                              authentication_form=form,
                                                              extra_context=context,
                                                              **kwargs)'''
                                #LOG.info("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
                                #LOG.info(template_name)
                                #LOG.info(request)
                                #LOG.info(request.META)
                                #LOG.info(request.POST)
                                #LOG.info(request.POST["password"])
                                return res

                    # user need to activate account by email link first
                    else:
                        activate_first = "Please check your email to activate your login account first."
                        login_url = "/auth/login/"

                        res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                        res.set_cookie('login_failed_reason', activate_first, max_age=10)
                        res.set_cookie('login_failed_status', "not activate", max_age=10)

                        '''login = {'activate_first': activate_first}
                        context = {
                            'login': login,
                        }

                        res = django_auth_views.login(request,
                                                      template_name=template_name,
                                                      authentication_form=form,
                                                      extra_context=context,
                                                      **kwargs)'''
                        return res

    res = django_auth_views.login(request,
                                  template_name=template_name,
                                  authentication_form=form,
                                  extra_context=extra_context,
                                  **kwargs)

    #LOG.info("res of openstack_auth/views.py login is")
    #LOG.info(res)
    # Save the region in the cookie, this is used as the default
    # selected region next time the Login form loads.
    if request.method == "POST":

        #LOG.info("go into if request.method == POST")

        utils.set_response_cookie(res, 'login_region',
                                  request.POST.get('region', ''))
        utils.set_response_cookie(res, 'login_domain',
                                  request.POST.get('domain', ''))


    # Set the session data here because django's session key rotation
    # will erase it if we set it earlier.

    #LOG.info("---------------------------------------------------------------------------------------------")
    if request.user.is_authenticated():
        LOG.info("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        for key, value in request.session.items():
            LOG.info('{} => {}'.format(key, value))

        #LOG.info("---------------------------------------------------------------------------------------------")
        #LOG.info(request.user)
        if request.method == "POST":
            c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                  password="password", project_domain_id="default", project_domain_name="Default",
                                  project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                  user_domain_id="default",
                                  user_domain_name="Default", username="zun", region_name="RegionOne",
                                  service_name="zun",
                                  service_type="container")

            user_name = request.user.username
            #LOG.info("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
            #LOG.info(user_name)
            #LOG.info(request.META)

            get_user = c.users.list(None, None, None, None)
            uuid = get_list_user_uuid(get_user, user_name)

            #there are several users that are not in zun database, but in keystone database. they can be authenticated either!
            if uuid is not None:

                # this is the previous status of user in database, not the current status!
                #userinfo = c.users.get(uuid)

                # update last_login_time as long as users tried to login
                '''last_login_time = datetime.now()
                user_update_info_zun = {'last_login_time': last_login_time}

                args, run = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

                update_response = c.users.update(uuid, **args)
                LOG.info("xxxxxx signup update response xxxxxx")
                LOG.info(update_response)

                # check whether user attempt to login too often
                if userinfo.last_login_time is not None:
                    naive_userinfo = userinfo.last_login_time.split("+")[0]
                    naive_userinfo = datetime.strptime(naive_userinfo, "%Y-%m-%d %H:%M:%S")

                    time_difference = last_login_time - naive_userinfo
                    LOG.info("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

                    LOG.info(time_difference)

                    time_interval = 4 ** userinfo.failed_attempt
                    if time_difference.seconds <= time_interval:
                        forbid_login = "Please wait " + str(time_interval) + " seconds for next login attempt."
                        login = {'forbid_login': forbid_login}
                        context = {
                            'login': login,
                        }

                        res = django_auth_views.login(request,
                                                      template_name=template_name,
                                                      authentication_form=form,
                                                      extra_context=context,
                                                      **kwargs)
                        return res'''

                last_success_login_ip = request.META["REMOTE_ADDR"]

                user_update_info_zun = {'failed_attempt': 0, 'last_success_login_ip': last_success_login_ip}

                args, run = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

                c.users.update(uuid, **args)
                #LOG.info("xxxxxx signup update response xxxxxx")
                #LOG.info(update_response)

        auth_user.set_session_from_user(request, request.user)
        regions = dict(forms.Login.get_region_choices())
        region = request.user.endpoint
        login_region = request.POST.get('region')
        region_name = regions.get(login_region)
        request.session['region_endpoint'] = region
        request.session['region_name'] = region_name
        expiration_time = request.user.time_until_expiration()
        threshold_days = getattr(
            settings, 'PASSWORD_EXPIRES_WARNING_THRESHOLD_DAYS', -1)
        if expiration_time is not None and \
                expiration_time.days <= threshold_days:

            LOG.info("go into if expiration_time is not None and \
                expiration_time.days <= threshold_days:")

            expiration_time = str(expiration_time).rsplit(':', 1)[0]
            msg = (_('Please consider changing your password, it will expire'
                     ' in %s minutes') %
                   expiration_time).replace(':', ' Hours and ')
            messages.warning(request, msg)

    else:
        #LOG.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #LOG.info(request.user)
        if request.method == "POST":
            form_failed_attempt = UserLoginForm(request.POST)
            #LOG.info("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
            #LOG.info(form_failed_attempt)
            #LOG.info(form_failed_attempt.is_valid())
            if form_failed_attempt.is_valid():
                username = form_failed_attempt.cleaned_data.get('username')
                c = zun_client.Client(auth_url="http://keystone.nova.svc.cluster.local:80/v3",
                                      password="password", project_domain_id="default", project_domain_name="Default",
                                      project_id="43d0ef3a4b5d4a49bfb847f84ee2ec5c", project_name="service",
                                      user_domain_id="default",
                                      user_domain_name="Default", username="zun", region_name="RegionOne",
                                      service_name="zun",
                                      service_type="container")

                #LOG.info("llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
                #LOG.info(username)

                get_user = c.users.list(None, None, None, None)
                uuid = get_list_user_uuid(get_user, username)

                if uuid is None:

                    not_exist = "User " + username + " does not exist. Please register!"

                    login_url = "/auth/login/"

                    res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                    res.set_cookie('login_failed_reason', not_exist, max_age=10)
                    res.set_cookie('login_failed_status', "not exist", max_age=10)

                    '''login = {'not_exist': not_exist}
                    context = {
                        'login': login,
                    }

                    res = django_auth_views.login(request,
                                                  template_name=template_name,
                                                  authentication_form=form,
                                                  extra_context=context,
                                                  **kwargs)'''
                    return res

                else:
                    #this is the previous status of user in database, not the current status!
                    userinfo = c.users.get(uuid)
                    #this means the account has already been activated by email link
                    if userinfo.account_status == 0:

                        #update last_login_time as long as users tried to login
                        '''last_login_time = datetime.now()
                        user_update_info_zun = {'last_login_time': last_login_time}

                        args, run = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)

                        update_response = c.users.update(uuid, **args)
                        LOG.info("xxxxxx signup update response xxxxxx")
                        LOG.info(update_response)

                        #check whether user attempt to login too often
                        if userinfo.last_login_time is not None:
                            naive_userinfo = userinfo.last_login_time.split("+")[0]
                            naive_userinfo = datetime.strptime(naive_userinfo, "%Y-%m-%d %H:%M:%S")

                            time_difference = last_login_time - naive_userinfo
                            LOG.info("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

                            LOG.info(time_difference)

                            time_interval = 4 ** userinfo.failed_attempt
                            if time_difference.seconds <= time_interval:
                                forbid_login = "Please wait " + str(time_interval) + " seconds for next login attempt."
                                login = {'forbid_login': forbid_login}
                                context = {
                                    'login': login,
                                }

                                res = django_auth_views.login(request,
                                                              template_name=template_name,
                                                              authentication_form=form,
                                                              extra_context=context,
                                                              **kwargs)
                                return res'''

                        #check whether users failed to login too many times
                        prev_failed_attempt = userinfo.failed_attempt
                        prev_failed_attempt += 1
                        threshold = 5

                        if prev_failed_attempt >= threshold:
                            must_passreset = "You have failed to login too many times! Please reset your password!"
                            login_url = "/auth/passwordreset/"

                            res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                            res.set_cookie('login_failed_reason', must_passreset, max_age=10)
                            res.set_cookie('login_failed_status', "must passreset", max_age=10)
                            return res

                            #return redirect("/auth/passwordreset/")

                        remain = threshold - prev_failed_attempt

                        '''login = {'username': username, 'remain_attempt': remain_attempt}
                        context = {
                            'login': login,
                        }'''

                        last_failed_login_ip = request.META["REMOTE_ADDR"]

                        user_update_info_zun = {'failed_attempt': prev_failed_attempt, 'last_failed_login_ip': last_failed_login_ip}
                        args2, run2 = _cleanup_user_params(USER_CREATE_ATTRS, True, **user_update_info_zun)
                        c.users.update(uuid, **args2)
                        #LOG.info("xxxxxx signup update response xxxxxx")
                        #LOG.info(update_response)

                        remain_attempt = "Invalid credential. You have " + str(remain) + \
                                         " chances remain to login. Please input username and password correctly."

                        login_url = "/auth/login/"

                        res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                        res.set_cookie('login_failed_reason', remain_attempt, max_age=10)
                        res.set_cookie('login_failed_status', "remain attempt", max_age=10)

                        '''res = django_auth_views.login(request,
                                                      template_name=template_name,
                                                      authentication_form=form,
                                                      extra_context=context,
                                                      **kwargs)'''
                        return res
                        #return render(request, 'auth/login.html', context)
                        #return shortcuts.redirect('/auth/login/', context)

                    else:
                        activate_first = "Please check your email to activate your login account first."

                        login_url = "/auth/login/"

                        res = django_auth_views.logout_then_login(request, login_url=login_url, **kwargs)
                        res.set_cookie('login_failed_reason', activate_first, max_age=10)
                        res.set_cookie('login_failed_status', "not activate", max_age=10)

                        '''login = {'activate_first': activate_first}
                        context = {
                            'login': login,
                        }

                        res = django_auth_views.login(request,
                                                      template_name=template_name,
                                                      authentication_form=form,
                                                      extra_context=context,
                                                      **kwargs)'''
                        return res
    #LOG.info("222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222")
    #LOG.info(res)
    #LOG.info("222before return res222")
    #LOG.info(request.user.username)

    #res = shortcuts.redirect(horizon.get_user_home(request.user))

    #return redirect("/index/")
    return res


@sensitive_post_parameters()
@csrf_exempt
@never_cache
def websso(request):
    """Logs a user in using a token from Keystone's POST."""
    referer = request.META.get('HTTP_REFERER', settings.OPENSTACK_KEYSTONE_URL)
    auth_url = utils.clean_up_auth_url(referer)
    token = request.POST.get('token')

    #LOG.info("xxx enter websso xxxxxx")

    try:
        request.user = auth.authenticate(request=request, auth_url=auth_url,
                                         token=token)
    except exceptions.KeystoneAuthException as exc:
        msg = 'Login failed: %s' % six.text_type(exc)
        res = django_http.HttpResponseRedirect(settings.LOGIN_URL)
        res.set_cookie('logout_reason', msg, max_age=10)
        return res

    auth_user.set_session_from_user(request, request.user)
    auth.login(request, request.user)
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    return django_http.HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


def logout(request, login_url=None, **kwargs):
    """Logs out the user if he is logged in. Then redirects to the log-in page.

    :param login_url:
        Once logged out, defines the URL where to redirect after login

    :param kwargs:
        see django.contrib.auth.views.logout_then_login extra parameters.

    """
    msg = 'Logging out user "%(username)s".' % \
        {'username': request.user.username}
    LOG.info(msg)

    """ Securely logs a user out. """
    return django_auth_views.logout_then_login(request, login_url=login_url,
                                               **kwargs)


def delete_token(endpoint, token_id):
    """Delete a token."""
    LOG.warning("The delete_token method is deprecated and now does nothing")


@login_required
def switch(request, tenant_id, redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """Switches an authenticated user from one project to another."""
    LOG.debug('Switching to tenant %s for user "%s".',
              (tenant_id, request.user.username))

    endpoint, __ = utils.fix_auth_url_version_prefix(request.user.endpoint)
    session = utils.get_session()
    # Keystone can be configured to prevent exchanging a scoped token for
    # another token. Always use the unscoped token for requesting a
    # scoped token.
    unscoped_token = request.user.unscoped_token
    auth = utils.get_token_auth_plugin(auth_url=endpoint,
                                       token=unscoped_token,
                                       project_id=tenant_id)

    try:
        auth_ref = auth.get_access(session)
        msg = 'Project switch successful for user "%(username)s".' % \
            {'username': request.user.username}
        LOG.info(msg)
    except keystone_exceptions.ClientException:
        msg = (
            _('Project switch failed for user "%(username)s".') %
            {'username': request.user.username})
        messages.error(request, msg)
        auth_ref = None
        LOG.exception('An error occurred while switching sessions.')

    # Ensure the user-originating redirection url is safe.
    # Taken from django.contrib.auth.views.login()
    redirect_to = request.GET.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL

    if auth_ref:
        user = auth_user.create_user_from_token(
            request,
            auth_user.Token(auth_ref, unscoped_token=unscoped_token),
            endpoint)
        auth_user.set_session_from_user(request, user)
        message = (
            _('Switch to project "%(project_name)s" successful.') %
            {'project_name': request.user.project_name})
        messages.success(request, message)
    response = shortcuts.redirect(redirect_to)
    utils.set_response_cookie(response, 'recent_project',
                              request.user.project_id)
    return response


@login_required
def switch_region(request, region_name,
                  redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """Switches the user's region for all services except Identity service.

    The region will be switched if the given region is one of the regions
    available for the scoped project. Otherwise the region is not switched.
    """
    if region_name in request.user.available_services_regions:
        request.session['services_region'] = region_name
        LOG.debug('Switching services region to %s for user "%s".',
                  (region_name, request.user.username))

    redirect_to = request.GET.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL

    response = shortcuts.redirect(redirect_to)
    utils.set_response_cookie(response, 'services_region',
                              request.session['services_region'])
    return response


@login_required
def switch_keystone_provider(request, keystone_provider=None,
                             redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """Switches the user's keystone provider using K2K Federation

    If keystone_provider is given then we switch the user to
    the keystone provider using K2K federation. Otherwise if keystone_provider
    is None then we switch the user back to the Identity Provider Keystone
    which a non federated token auth will be used.
    """
    base_token = request.session.get('k2k_base_unscoped_token', None)
    k2k_auth_url = request.session.get('k2k_auth_url', None)
    keystone_providers = request.session.get('keystone_providers', None)

    if not base_token or not k2k_auth_url:
        msg = _('K2K Federation not setup for this session')
        raise exceptions.KeystoneAuthException(msg)

    redirect_to = request.GET.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL

    unscoped_auth_ref = None
    keystone_idp_id = getattr(
        settings, 'KEYSTONE_PROVIDER_IDP_ID', 'localkeystone')

    if keystone_provider == keystone_idp_id:
        current_plugin = plugin.TokenPlugin()
        unscoped_auth = current_plugin.get_plugin(auth_url=k2k_auth_url,
                                                  token=base_token)
    else:
        # Switch to service provider using K2K federation
        plugins = [plugin.TokenPlugin()]
        current_plugin = plugin.K2KAuthPlugin()

        unscoped_auth = current_plugin.get_plugin(
            auth_url=k2k_auth_url, service_provider=keystone_provider,
            plugins=plugins, token=base_token)

    try:
        # Switch to identity provider using token auth
        unscoped_auth_ref = current_plugin.get_access_info(unscoped_auth)
    except exceptions.KeystoneAuthException as exc:
        msg = 'Switching to Keystone Provider %s has failed. %s' \
              % (keystone_provider, (six.text_type(exc)))
        messages.error(request, msg)

    if unscoped_auth_ref:
        try:
            request.user = auth.authenticate(
                request=request, auth_url=unscoped_auth.auth_url,
                token=unscoped_auth_ref.auth_token)
        except exceptions.KeystoneAuthException as exc:
            msg = 'Keystone provider switch failed: %s' % six.text_type(exc)
            res = django_http.HttpResponseRedirect(settings.LOGIN_URL)
            res.set_cookie('logout_reason', msg, max_age=10)
            return res
        auth.login(request, request.user)
        auth_user.set_session_from_user(request, request.user)
        request.session['keystone_provider_id'] = keystone_provider
        request.session['keystone_providers'] = keystone_providers
        request.session['k2k_base_unscoped_token'] = base_token
        request.session['k2k_auth_url'] = k2k_auth_url
        message = (
            _('Switch to Keystone Provider "%(keystone_provider)s"'
              'successful.') % {'keystone_provider': keystone_provider})
        messages.success(request, message)

    response = shortcuts.redirect(redirect_to)
    return response
