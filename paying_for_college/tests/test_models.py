#!/usr/bin/env python
# -*- coding: utf8 -*-
import datetime
import dateutil.parser
import smtplib

import mock
from mock import mock_open, patch
import requests

from django.test import TestCase
from paying_for_college.models import (
    School, Contact, Program, Alias, Nickname, Feedback)
from paying_for_college.models import ConstantCap, ConstantRate, Disclosure
from paying_for_college.models import Notification, print_vals
from paying_for_college.models import get_region, make_divisible_by_6


class MakeDivisibleTest(TestCase):

    def test_make_divisible(self):
        test_value = ''
        self.assertTrue(make_divisible_by_6(test_value) == test_value)
        test_value = 0
        self.assertTrue(make_divisible_by_6(test_value) == test_value)
        test_value = 1
        self.assertTrue(make_divisible_by_6(test_value) == 6)
        test_value = 3
        self.assertTrue(make_divisible_by_6(test_value) == 6)
        test_value = 45
        self.assertTrue(make_divisible_by_6(test_value) == 48)


class SchoolRegionTest(TestCase):

    def test_get_region(self):
        school = School(school_id='123456', state='NE')
        self.assertTrue(get_region(school) == 'MW')

    def test_get_region_failure(self):
        school = School(school_id='123456', state='')
        self.assertTrue(get_region(school) == '')


class SchoolModelsTest(TestCase):

    def create_school(
            self, ID=999999,
            data_json='',
            accreditor="Almighty Wizard",
            city="Emerald City",
            degrees_highest="3",
            state="OZ",
            ope6=5555,
            ope8=555500):
        return School.objects.create(
            school_id=ID,
            data_json=data_json,
            accreditor=accreditor,
            degrees_highest=degrees_highest,
            degrees_predominant=degrees_highest,
            city=city,
            state=state,
            ope6_id=ope6,
            ope8_id=ope8)

    def create_alias(
            self, alias, school):
        return Alias.objects.create(
            alias=alias,
            is_primary=True,
            institution=school)

    def create_contact(self):
        return Contact.objects.create(
            contacts='hack@hackey.edu',
            name='Hackey Sack',
            endpoint=u'endpoint.hackey.edu')

    def create_nickname(self, school):
        return Nickname.objects.create(
            institution=school,
            nickname='Hackers')

    def create_program(self, school):
        return Program.objects.create(
            institution=school,
            program_name='Hacking',
            level='3')

    def create_disclosure(self, school):
        return Disclosure.objects.create(
            institution=school,
            name='Regional transferability',
            text="Your credits won't transfer")

    def create_notification(
            self,
            school,
            oid='f38283b5b7c939a058889f997949efa566c616c5',
            time='2016-01-13T20:06:18.913112+00:00'):
        return Notification.objects.create(
            institution=school,
            oid=oid,
            timestamp=dateutil.parser.parse(time),
            errors='none')

    def create_feedback(self):
        return Feedback.objects.create(
            created=datetime.datetime.now(),
            message='Thank you, FPO',
            url=('www.cfpb.gov/paying-for-college2/'
                 'understanding-your-financial-aid-offer/offer/'
                 '?iped=451796&pid=2736'
                 '&oid=1234567890123456789012345678901234567890'
                 '&book=1832&gib=0&gpl=0&hous=4431&insi=3.36&insl=4339'
                 '&inst=35&leng=0&mta=0&othg=0&othr=2517&parl=0&pelg=2070'
                 '&perl=0&ppl=0&prvl=0&prvf=0&prvi=0&schg=2444&stag=0'
                 '&subl=3464&totl=81467&tran=1503&tuit=16107&unsl=5937'))

    def test_school_related_models(self):
        s = self.create_school()
        self.assertTrue(isinstance(s, School))
        self.assertEqual(s.primary_alias, "Not Available")
        d = self.create_disclosure(s)
        self.assertTrue(isinstance(d, Disclosure))
        self.assertIn(d.name, d.__unicode__())
        a = self.create_alias('Wizard U', s)
        self.assertTrue(isinstance(a, Alias))
        self.assertIn(a.alias, a.__unicode__())
        self.assertEqual(s.primary_alias, a.alias)
        self.assertEqual(s.__unicode__(), a.alias + u" (%s)" % s.school_id)
        c = self.create_contact()
        self.assertTrue(isinstance(c, Contact))
        self.assertIn(c.contacts, c.__unicode__())
        n = self.create_nickname(s)
        self.assertTrue(isinstance(n, Nickname))
        self.assertIn(n.nickname, n.__unicode__())
        self.assertIn(n.nickname, s.nicknames)
        p = self.create_program(s)
        self.assertTrue(isinstance(p, Program))
        self.assertIn(p.program_name, p.__unicode__())
        self.assertIn(p.program_name, p.as_json())
        self.assertIn('Bachelor', p.get_level())
        noti = self.create_notification(s)
        self.assertTrue(isinstance(noti, Notification))
        self.assertIn(noti.oid, noti.__unicode__())
        self.assertIsInstance(print_vals(s, noprint=True), basestring)
        self.assertIn(
            'Emerald City',
            print_vals(s, val_list=True, noprint=True)
        )
        self.assertIn(
            "Emerald City",
            print_vals(s, val_dict=True, noprint=True)['city'])
        self.assertTrue("Emerald City" in print_vals(s, noprint=True))

        print_patcher = mock.patch('paying_for_college.models.print')
        with print_patcher as mock_print:
            self.assertIsInstance(print_vals(s, val_list=True), list)
            self.assertTrue(mock_print.called)

        with print_patcher as mock_print:
            self.assertIsNone(print_vals(s))
            self.assertTrue(mock_print.called)

        self.assertTrue(s.convert_ope6() == '005555')
        self.assertTrue(s.convert_ope8() == '00555500')
        self.assertTrue('Bachelor' in s.get_highest_degree())
        s.ope6_id = 555555
        s.ope8_id = 55555500
        self.assertTrue(s.convert_ope6() == '555555')
        self.assertTrue(s.convert_ope8() == '55555500')
        s.ope6_id = None
        s.ope8_id = None
        self.assertTrue(s.convert_ope6() == '')
        self.assertTrue(s.convert_ope8() == '')

    def test_constant_models(self):
        cr = ConstantRate(name='cr test', slug='crTest', value='0.1')
        self.assertTrue(cr.__unicode__() == u'cr test (crTest), updated None')
        cc = ConstantCap(name='cc test', slug='ccTest', value='0')
        self.assertTrue(cc.__unicode__() == u'cc test (ccTest), updated None')

    @mock.patch('paying_for_college.models.send_mail')
    def test_email_notification(self, mock_mail):
        skul = self.create_school()
        skul.settlement_school = 'edmc'
        noti = self.create_notification(skul)
        msg = noti.notify_school()
        self.assertTrue('failed' in msg)
        contact = self.create_contact()
        contact.endpoint = ''
        contact.save()
        skul.contact = contact
        skul.save()
        noti2 = self.create_notification(skul)
        msg1 = noti2.notify_school()
        self.assertTrue(mock_mail.call_count == 1)
        self.assertTrue('email' in msg1)
        noti3 = self.create_notification(skul)
        mock_mail.side_effect = smtplib.SMTPException('fail')
        msg = noti3.notify_school()
        self.assertTrue(mock_mail.call_count == 2)

    @mock.patch('paying_for_college.models.requests.post')
    def test_endpoint_notification(self, mock_post):
        skul = self.create_school()
        skul.settlement_school = 'edmc'
        contact = self.create_contact()
        contact.endpoint = u'fake-api.fakeschool.edu'
        contact.save()
        skul.contact = contact
        skul.save()
        noti = self.create_notification(skul)
        msg = noti.notify_school()
        self.assertTrue(mock_post.call_count == 1)
        self.assertTrue('endpoint' in msg)
        mock_return = mock.Mock()
        mock_return.ok = False
        mock_post.return_value = mock_return
        fail_msg = noti.notify_school()
        self.assertTrue('fail' in fail_msg)

    def test_endpoint_notification_blank_contact(self):
        skul = self.create_school()
        skul.settlement_school = 'edmc'
        contact = self.create_contact()
        contact.contacts = ''
        contact.endpoint = ''
        contact.save()
        skul.contact = contact
        skul.save()
        noti = self.create_notification(skul)
        msg = noti.notify_school()
        self.assertTrue('failed' in msg)

    @mock.patch('paying_for_college.models.requests.post')
    def test_notification_request_errors(self, mock_post):
        skul = self.create_school()
        skul.settlement_school = 'edmc'
        contact = self.create_contact()
        skul.contact = contact
        skul.save()
        noti = self.create_notification(skul)
        mock_post.side_effect = requests.exceptions.ConnectionError
        msg = noti.notify_school()
        self.assertTrue('Error' in msg)
        mock_post.side_effect = requests.exceptions.Timeout
        msg = noti.notify_school()
        self.assertTrue('Error' in msg)
        mock_post.side_effect = requests.exceptions.RequestException
        msg = noti.notify_school()
        self.assertTrue('Error' in msg)

    def test_feedback_parsed_url(self):
        sorted_keys = ['book', 'gib', 'gpl', 'hous', 'insi', 'insl', 'inst',
                       'iped', 'leng', 'mta', 'oid', 'othg', 'othr', 'parl',
                       'pelg', 'perl', 'pid', 'ppl', 'prvf', 'prvi', 'prvl',
                       'schg', 'stag', 'subl', 'totl', 'tran', 'tuit', 'unsl']
        feedback = self.create_feedback()
        self.assertEqual(
            sorted(feedback.parsed_url.keys()),
            sorted_keys)
        self.assertEqual(
            feedback.parsed_url['iped'], '451796')
        self.assertEqual(
            feedback.parsed_url['oid'],
            '1234567890123456789012345678901234567890')
        feedback.url = feedback.url.split('?')[0]
        self.assertEqual(feedback.parsed_url, {})
        feedback.url = 'www.cfpb.gov/feedback/'
        self.assertEqual(feedback.parsed_url, {})

    def test_feedback_school(self):
        school = self.create_school(ID=451796)
        feedback = self.create_feedback()
        self.assertEqual(feedback.school, school)
        feedback.url = feedback.url.replace("iped=451796&", '')
        self.assertEqual(feedback.school, None)
        feedback.url = ''
        self.assertEqual(feedback.school, None)

    def test_feedback_unmet_cost(self):
        feedback = self.create_feedback()
        self.assertEqual(feedback.unmet_cost, 8136)
        feedback.url = feedback.url.replace('&book=1832', '&book=voodoo')
        self.assertEqual(feedback.unmet_cost, 6304)
        feedback.url = feedback.url.replace('offer', 'feedback')
        self.assertIs(feedback.unmet_cost, None)

    def test_feedback_cost_error_valid_values(self):
        feedback = self.create_feedback()
        self.assertEqual(feedback.cost_error, 0)

    def test_feedback_cost_error_true(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('totl=81467', 'totl=1000')
        self.assertEqual(feedback.cost_error, 1)

    def test_feedback_cost_error_blank_totl(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('totl=81467', 'totl=')
        self.assertEqual(feedback.cost_error, 1)

    def test_feedback_cost_error_blank_tuition(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('tuit=16107', 'tuit=')
        self.assertEqual(feedback.cost_error, 0)

    def test_feedback_cost_error_missing_tuit_field(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('&tuit=16107', '')
        self.assertEqual(feedback.cost_error, 0)

    def test_feedback_cost_error_missing_totl_field(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('&totl=81467', '')
        self.assertEqual(feedback.cost_error, 1)

    def test_feedback_cost_error_missing_totl_and_tuit_fields(self):
        feedback = self.create_feedback()
        feedback.url = feedback.url.replace('&tuit=16107', '')
        feedback.url = feedback.url.replace('&totl=81467', '')
        self.assertEqual(feedback.cost_error, 0)

    def test_feedback_cost_error_missing_url(self):
        feedback = self.create_feedback()
        feedback.url = ''
        self.assertEqual(feedback.cost_error, 0)

    def test_feedback_tuition_plan(self):
        feedback = self.create_feedback()
        self.assertEqual(feedback.tuition_plan, 4339)
        feedback.url = feedback.url.replace('insl=4339', 'insl=a')
        self.assertEqual(feedback.tuition_plan, None)
        feedback.url = feedback.url.replace('insl=a', 'insl=')
        self.assertEqual(feedback.tuition_plan, None)


class NonSettlementNotificaion(TestCase):
    fixtures = ['test_fixture.json']

    def create_notification(self,
                            school,
                            oid='f38283b5b7c939a058889f997949efa566c616c5',
                            time='2016-01-13T20:06:18.913112+00:00'):
        return Notification.objects.create(
            institution=school,
            oid=oid,
            timestamp=dateutil.parser.parse(time),
            errors='none')

    def test_nonsettlement_notification(self):
        skul = School.objects.get(pk=155317)  # a non-settlement school
        notification = self.create_notification(skul)
        non_msg = notification.notify_school()
        self.assertTrue('No notification required' in non_msg)


class ProgramExport(TestCase):
    fixtures = ['test_program.json']

    def test_program_as_csv(self):
        p = Program.objects.get(pk=1)
        m = mock_open()
        with patch("__builtin__.open", m, create=True):
            p.as_csv('/tmp.csv')
        self.assertTrue(m.call_count == 1)
