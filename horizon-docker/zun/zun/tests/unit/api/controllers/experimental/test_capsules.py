#    Copyright 2017 Arm Limited
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from mock import patch
from webtest.app import AppError
from zun.common import exception
from zun.tests.unit.api import base as api_base


class TestCapsuleController(api_base.FunctionalTest):
    @patch('zun.compute.api.API.capsule_create')
    def test_create_capsule(self, mock_capsule_create):
        params = ('{"spec": {"kind": "capsule",'
                  '"spec": {"containers":'
                  '[{"environment": {"ROOT_PASSWORD": "foo0"}, '
                  '"image": "test", "labels": {"app": "web"}, '
                  '"image_driver": "docker", "resources": '
                  '{"allocation": {"cpu": 1, "memory": 1024}}}], '
                  '"volumes": [{"name": "volume1", '
                  '"image": "test", "drivers": "cinder", "volumeType": '
                  '"type1", "driverOptions": "options", '
                  '"size": "5GB"}]}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}, '
                  '{"foo1": "bar1"}], '
                  '"name": "capsule-example"}}}')
        response = self.app.post('/capsules/',
                                 params=params,
                                 content_type='application/json')
        return_value = response.json
        expected_meta_name = "capsule-example"
        expected_meta_label = [{"foo0": "bar0"}, {"foo1": "bar1"}]
        expected_container_num = 2
        self.assertEqual(len(return_value["containers_uuids"]),
                         expected_container_num)
        self.assertEqual(return_value["meta_name"], expected_meta_name)
        self.assertEqual(return_value["meta_labels"], expected_meta_label)
        self.assertEqual(202, response.status_int)
        self.assertTrue(mock_capsule_create.called)

    @patch('zun.compute.api.API.capsule_create')
    def test_create_capsule_two_containers(self, mock_capsule_create):
        params = ('{"spec": {"kind": "capsule",'
                  '"spec": {"containers":'
                  '[{"environment": {"ROOT_PASSWORD": "foo0"}, '
                  '"image": "test1", "labels": {"app0": "web0"}, '
                  '"image_driver": "docker", "resources": '
                  '{"allocation": {"cpu": 1, "memory": 1024}}}, '
                  '{"environment": {"ROOT_PASSWORD": "foo1"}, '
                  '"image": "test1", "labels": {"app1": "web1"}, '
                  '"image_driver": "docker", "resources": '
                  '{"allocation": {"cpu": 1, "memory": 1024}}}]}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}, '
                  '{"foo1": "bar1"}], '
                  '"name": "capsule-example"}}}')
        response = self.app.post('/capsules/',
                                 params=params,
                                 content_type='application/json')
        return_value = response.json
        expected_meta_name = "capsule-example"
        expected_meta_label = [{"foo0": "bar0"}, {"foo1": "bar1"}]
        expected_container_num = 3
        self.assertEqual(len(return_value["containers_uuids"]),
                         expected_container_num)
        self.assertEqual(return_value["meta_name"],
                         expected_meta_name)
        self.assertEqual(return_value["meta_labels"],
                         expected_meta_label)
        self.assertEqual(202, response.status_int)
        self.assertTrue(mock_capsule_create.called)

    @patch('zun.compute.api.API.capsule_create')
    @patch('zun.common.utils.check_capsule_template')
    def test_create_capsule_wrong_kind_set(self, mock_check_template,
                                           mock_capsule_create):
        params = ('{"spec": {"kind": "test",'
                  '"spec": {"containers":'
                  '[{"environment": {"ROOT_PASSWORD": "foo0"}, '
                  '"image": "test1", "labels": {"app0": "web0"}, '
                  '"image_driver": "docker", "resources": '
                  '{"allocation": {"cpu": 1, "memory": 1024}}}]}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}], '
                  '"name": "capsule-example"}}}')
        mock_check_template.side_effect = exception.InvalidCapsuleTemplate(
            "kind fields need to be set as capsule or Capsule")
        response = self.post_json('/capsules/', params, expect_errors=True)
        self.assertEqual(400, response.status_int)
        self.assertFalse(mock_capsule_create.called)

    @patch('zun.compute.api.API.capsule_create')
    @patch('zun.common.utils.check_capsule_template')
    def test_create_capsule_less_than_one_container(self, mock_check_template,
                                                    mock_capsule_create):
        params = ('{"spec": {"kind": "capsule",'
                  '"spec": {container:[]}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}], '
                  '"name": "capsule-example"}}}')
        mock_check_template.side_effect = exception.InvalidCapsuleTemplate(
            "Capsule need to have one container at least")
        response = self.post_json('/capsules/', params, expect_errors=True)
        self.assertEqual(400, response.status_int)
        self.assertFalse(mock_capsule_create.called)

    @patch('zun.compute.api.API.capsule_create')
    @patch('zun.common.utils.check_capsule_template')
    def test_create_capsule_no_container_field(self, mock_check_template,
                                               mock_capsule_create):
        params = ('{"spec": {"kind": "capsule",'
                  '"spec": {}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}], '
                  '"name": "capsule-example"}}}')
        mock_check_template.side_effect = exception.InvalidCapsuleTemplate(
            "Capsule need to have one container at least")
        self.assertRaises(AppError, self.app.post, '/capsules/',
                          params=params, content_type='application/json')
        self.assertFalse(mock_capsule_create.called)

    @patch('zun.compute.api.API.capsule_create')
    @patch('zun.common.utils.check_capsule_template')
    def test_create_capsule_no_container_image(self, mock_check_template,
                                               mock_capsule_create):
        params = ('{"spec": {"kind": "capsule",'
                  '"spec": {container:[{"environment": '
                  '{"ROOT_PASSWORD": "foo1"}]}, '
                  '"metadata": {"labels": [{"foo0": "bar0"}], '
                  '"name": "capsule-example"}}}')
        mock_check_template.side_effect = exception.InvalidCapsuleTemplate(
            "Container image is needed")
        self.assertRaises(AppError, self.app.post, '/capsules/',
                          params=params, content_type='application/json')
        self.assertFalse(mock_capsule_create.called)
