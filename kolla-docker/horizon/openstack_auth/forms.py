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

from __future__ import unicode_literals

import collections
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import forms as django_auth_forms
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from openstack_auth import exceptions
from openstack_auth import utils
from django import forms
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.models import User

from django.db import models
from django.forms import ModelForm

LOG = logging.getLogger(__name__)



try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict

from django import forms
from django.utils.translation import ugettext_lazy as _

from .fields import (CreditCardNumberField, CreditCardExpiryField,
                     CreditCardVerificationField, CreditCardNameField)


class PaymentForm(forms.Form):
    '''
    Payment form, suitable for Django templates.
    When displaying the form remember to use *action* and *method*.
    '''
    def __init__(self, data=None, action='', method='post', provider=None,
                 payment=None, hidden_inputs=True, autosubmit=False):
        if hidden_inputs and data is not None:
            super(PaymentForm, self).__init__(auto_id=False)
            for key, val in data.items():
                widget = forms.widgets.HiddenInput()
                self.fields[key] = forms.CharField(initial=val, widget=widget)
        else:
            super(PaymentForm, self).__init__(data=data)
        self.action = action
        self.autosubmit = autosubmit
        self.method = method
        self.provider = provider
        self.payment = payment


class CreditCardPaymentForm(PaymentForm):

    number = CreditCardNumberField(label=_('Card Number'), max_length=32,
                                   required=True)
    expiration = CreditCardExpiryField()
    cvv2 = CreditCardVerificationField(
        label=_('CVV2 Security Number'), required=False, help_text=_(
            'Last three digits located on the back of your card.'
            ' For American Express the four digits found on the front side.'))

    def __init__(self, *args, **kwargs):
        super(CreditCardPaymentForm, self).__init__(
            hidden_inputs=False, *args,  **kwargs)
        if hasattr(self, 'VALID_TYPES'):
            self.fields['number'].valid_types = self.VALID_TYPES


class CreditCardPaymentFormWithName(CreditCardPaymentForm):

    name = CreditCardNameField(label=_('Name on Credit Card'), max_length=128)

    def __init__(self, *args, **kwargs):
        super(CreditCardPaymentFormWithName, self).__init__(*args, **kwargs)
        name_field = self.fields.pop('name')
        fields = OrderedDict({'name': name_field})
        fields.update(self.fields)
        self.fields = fields


from datetime import date, datetime
from calendar import monthrange

'''class CreditCardField(forms.IntegerField):
    @staticmethod
    def get_cc_type(number):
        """
        Gets credit card type given number. Based on values from Wikipedia page
        "Credit card number".
        http://en.wikipedia.org/w/index.php?title=Credit_card_number
        """
        number = str(number)
        #group checking by ascending length of number
        if len(number) == 13:
            if number[0] == "4":
                return "Visa"
        elif len(number) == 14:
            if number[:2] == "36":
                return "MasterCard"
        elif len(number) == 15:
            if number[:2] in ("34", "37"):
                return "American Express"
        elif len(number) == 16:
            if number[:4] == "6011":
                return "Discover"
            if number[:2] in ("51", "52", "53", "54", "55"):
                return "MasterCard"
            if number[0] == "4":
                return "Visa"
        return "Unknown"

    def clean(self, value):
        """Check if given CC number is valid and one of the
           card types we accept"""
        if value and (len(value) < 13 or len(value) > 16):
            raise forms.ValidationError("Please enter in a valid "+\
                "credit card number.")
        elif self.get_cc_type(value) not in ("Visa", "MasterCard",
                                             "American Express"):
            raise forms.ValidationError("Please enter in a Visa, "+\
                "Master Card, or American Express credit card number.")
        return super(CreditCardField, self).clean(value)


class CCExpWidget(forms.MultiWidget):
    """ Widget containing two select boxes for selecting the month and year"""
    def decompress(self, value):
        return [value.month, value.year] if value else [None, None]

    def format_output(self, rendered_widgets):
        html = u' / '.join(rendered_widgets)
        return u'<span style="white-space: nowrap">%s</span>' % html


class CCExpField(forms.MultiValueField):
    EXP_MONTH = [(x, x) for x in xrange(1, 13)]
    EXP_YEAR = [(x, x) for x in xrange(date.today().year,
                                       date.today().year + 15)]
    default_error_messages = {
        'invalid_month': u'Enter a valid month.',
        'invalid_year': u'Enter a valid year.',
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.ChoiceField(choices=self.EXP_MONTH,
                error_messages={'invalid': errors['invalid_month']}),
            forms.ChoiceField(choices=self.EXP_YEAR,
                error_messages={'invalid': errors['invalid_year']}),
        )
        super(CCExpField, self).__init__(fields, *args, **kwargs)
        self.widget = CCExpWidget(widgets =
            [fields[0].widget, fields[1].widget])

    def clean(self, value):
        exp = super(CCExpField, self).clean(value)
        if date.today() > exp:
            raise forms.ValidationError(
            "The expiration date you entered is in the past.")
        return exp

    def compress(self, data_list):
        if data_list:
            if data_list[1] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_year']
                raise forms.ValidationError(error)
            if data_list[0] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_month']
                raise forms.ValidationError(error)
            year = int(data_list[1])
            month = int(data_list[0])
            # find last day of the month
            day = monthrange(year, month)[1]
            return date(year, month, day)
        return None


class PaymentForm(forms.Form):
    number = CreditCardField(required = True, label = "Card Number")
    holder = forms.CharField(required = True, label = "Card Holder Name",
        max_length = 60)
    expiration = CCExpField(required = True, label = "Expiration")
    ccv_number = forms.IntegerField(required = True, label = "CCV Number",
        max_value = 9999, widget = forms.TextInput(attrs={'size': '4'}))

    def __init__(self, *args, **kwargs):
        self.payment_data = kwargs.pop('payment_data', None)
        super(PaymentForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned = super(PaymentForm, self).clean()
        if not self.errors:
            result = self.process_payment()
            if result and result[0] == 'Card declined':
                raise forms.ValidationError('Your credit card was declined.')
            elif result and result[0] == 'Processing error':
                raise forms.ValidationError(
                    'We encountered the following error while processing '+\
                    'your credit card: '+result[1])
        return cleaned

    def process_payment(self):
        if self.payment_data:
            # don't process payment if payment_data wasn't set
            datadict = self.cleaned_data
            datadict.update(self.payment_data)

            from virtualmerchant import VirtualMerchant
            vmerchant = VirtualMerchant(datadict)

            return vmerchant.process_virtualmerchant_payment()'''


'''class UserForm(models.Model):
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    #displayname = models.CharField(max_length=100)
    #password_confirm = forms.CharField(label='Confirm password', max_length=30)
    def __unicode__(self):
        return self.user_name

class SignUpForm(ModelForm):
    #user_name = EmailField(label='Your user_name', required=True)
    #password = CharField(label='Your password', required=True)
    #displayname = CharField(label='Your displayname', required=True)

    class Meta:
        model = UserForm
        fields = "__all__"'''

class PRF(models.Model):
    email = models.CharField(max_length=100)
    def __unicode__(self):
        return self.user_name

class PassResetForm(ModelForm):
    class Meta:
        model = PRF
        fields = "__all__"

class NPF(models.Model):
    new_password =  models.CharField(max_length=100)
    new_password_confirm = models.CharField(max_length=100)

class NewPassForm(ModelForm):
    class Meta:
        model = NPF
        fields = "__all__"

class USF(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class UserSignupForm(ModelForm):
    class Meta:
        model = USF
        fields = "__all__"

class ULF(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class UserLoginForm(ModelForm):
    class Meta:
        model = ULF
        fields = "__all__"

class UPF(models.Model):
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    card_no = models.CharField(max_length=200)
    billing_address_line1 = models.CharField(max_length=200)
    billing_address_line2 = models.CharField(max_length=200)
    billing_address_line3 = models.CharField(max_length=200)
    billing_address_apt_suite_no = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    expiration_date = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)

class UserPaymentsForm(ModelForm):
    class Meta:
        model = UPF
        fields = "__all__"

'''class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )'''



class Login(django_auth_forms.AuthenticationForm):
    """Form used for logging in a user.

    Handles authentication with Keystone by providing the domain name, username
    and password. A scoped token is fetched after successful authentication.

    A domain name is required if authenticating with Keystone V3 running
    multi-domain configuration.

    If the user authenticated has a default project set, the token will be
    automatically scoped to their default project.

    If the user authenticated has no default project set, the authentication
    backend will try to scope to the projects returned from the user's assigned
    projects. The first successful project scoped will be returned.

    Inherits from the base ``django.contrib.auth.forms.AuthenticationForm``
    class for added security features.
    """
    use_required_attribute = False
    region = forms.ChoiceField(label=_("Region"), required=False)
    username = forms.CharField(
        label=_("Email"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        fields_ordering = ['username', 'password', 'region']
        if getattr(settings,
                   'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT',
                   False):
            last_domain = self.request.COOKIES.get('login_domain', None)
            if getattr(settings,
                       'OPENSTACK_KEYSTONE_DOMAIN_DROPDOWN',
                       False):
                self.fields['domain'] = forms.ChoiceField(
                    label=_("Domain"),
                    initial=last_domain,
                    required=True,
                    choices=getattr(settings,
                                    'OPENSTACK_KEYSTONE_DOMAIN_CHOICES',
                                    ()))
            else:
                self.fields['domain'] = forms.CharField(
                    initial=last_domain,
                    label=_("Domain"),
                    required=True,
                    widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
            self.fields['username'].widget = forms.widgets.TextInput()
            fields_ordering = ['domain', 'username', 'password', 'region']
        self.fields['region'].choices = self.get_region_choices()
        if len(self.fields['region'].choices) == 1:
            self.fields['region'].initial = self.fields['region'].choices[0][0]
            self.fields['region'].widget = forms.widgets.HiddenInput()
        elif len(self.fields['region'].choices) > 1:
            self.fields['region'].initial = self.request.COOKIES.get(
                'login_region')

        # if websso is enabled and keystone version supported
        # prepend the websso_choices select input to the form
        if utils.is_websso_enabled():
            initial = getattr(settings, 'WEBSSO_INITIAL_CHOICE', 'credentials')
            self.fields['auth_type'] = forms.ChoiceField(
                label=_("Authenticate using"),
                choices=getattr(settings, 'WEBSSO_CHOICES', ()),
                required=False,
                initial=initial)
            # add auth_type to the top of the list
            fields_ordering.insert(0, 'auth_type')

        # websso is enabled, but keystone version is not supported
        elif getattr(settings, 'WEBSSO_ENABLED', False):
            msg = ("Websso is enabled but horizon is not configured to work " +
                   "with keystone version 3 or above.")
            LOG.warning(msg)
        self.fields = collections.OrderedDict(
            (key, self.fields[key]) for key in fields_ordering)

    @staticmethod
    def get_region_choices():
        default_region = (settings.OPENSTACK_KEYSTONE_URL, "Default Region")
        regions = getattr(settings, 'AVAILABLE_REGIONS', [])
        if not regions:
            regions = [default_region]
        return regions

    @sensitive_variables()
    def clean(self):
        default_domain = getattr(settings,
                                 'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
                                 'Default')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        region = self.cleaned_data.get('region')
        domain = self.cleaned_data.get('domain', default_domain)

        if not (username and password):
            # Don't authenticate, just let the other validators handle it.
            return self.cleaned_data

        try:
            self.user_cache = authenticate(request=self.request,
                                           username=username,
                                           password=password,
                                           user_domain_name=domain,
                                           auth_url=region)
            LOG.info('Login successful for user "%(username)s" using domain '
                     '"%(domain)s", remote address %(remote_ip)s.',
                     {'username': username, 'domain': domain,
                      'remote_ip': utils.get_client_ip(self.request)})
        except exceptions.KeystoneAuthException as exc:
            LOG.info('Login failed for user "%(username)s" using domain '
                     '"%(domain)s", remote address %(remote_ip)s.',
                     {'username': username, 'domain': domain,
                      'remote_ip': utils.get_client_ip(self.request)})
            raise forms.ValidationError(exc)
        if hasattr(self, 'check_for_test_cookie'):  # Dropped in django 1.7
            self.check_for_test_cookie()
        return self.cleaned_data

