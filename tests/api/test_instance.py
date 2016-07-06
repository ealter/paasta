# Copyright 2015-2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import marathon
import mock
from pyramid import testing

from paasta_tools import marathon_tools
from paasta_tools.api import settings
from paasta_tools.api.views.instance import instance_status
from paasta_tools.api.views.instance import marathon_job_status


@mock.patch('paasta_tools.api.views.instance.marathon_job_status', autospec=True)
@mock.patch('paasta_tools.api.views.instance.marathon_tools.get_matching_appids', autospec=True)
@mock.patch('paasta_tools.api.views.instance.marathon_tools.load_marathon_service_config', autospec=True)
@mock.patch('paasta_tools.api.views.instance.marathon_tools.load_marathon_config', autospec=True)
@mock.patch('paasta_tools.api.views.instance.validate_service_instance', autospec=True)
@mock.patch('paasta_tools.api.views.instance.get_actual_deployments', autospec=True)
def test_instances_status(
    mock_get_actual_deployments,
    mock_validate_service_instance,
    mock_load_marathon_config,
    mock_load_marathon_service_config,
    mock_get_matching_appids,
    mock_marathon_job_status,
):
    settings.cluster = 'fake_cluster'
    mock_get_actual_deployments.return_value = {'fake_cluster.fake_instance': 'GIT_SHA',
                                                'fake_cluster.fake_instance2': 'GIT_SHA',
                                                'fake_cluster2.fake_instance': 'GIT_SHA',
                                                'fake_cluster2.fake_instance2': 'GIT_SHA'}
    mock_validate_service_instance.return_value = 'marathon'
    mock_marathon_config = marathon_tools.MarathonConfig(
        {'url': 'fake_url', 'user': 'fake_user', 'password': 'fake_password'}
    )
    mock_load_marathon_config.return_value = mock_marathon_config
    mock_get_matching_appids.return_value = ['a', 'b']
    mock_service_config = marathon_tools.MarathonServiceConfig(
        service='fake_service',
        cluster='fake_cluster',
        instance='fake_instance',
        config_dict={'bounce_method': 'fake_bounce'},
        branch_dict={},
    )
    mock_load_marathon_service_config.return_value = mock_service_config
    mock_marathon_job_status.return_value = 'fake_marathon_status'

    request = testing.DummyRequest()
    request.matchdict = {'service': 'fake_service', 'instance': 'fake_instance'}

    response = instance_status(request)
    assert response['state'] == 'Bouncing (fake_bounce)'
    assert response['desired state'] == 'Started'

    # error case with a nonexistent instance
    request2 = testing.DummyRequest()
    request2.matchdict = {'service': 'fake_service', 'instance': 'bad_instance'}

    response2 = instance_status(request2)
    assert response2.status_int == 404


@mock.patch('paasta_tools.api.views.instance.marathon_tools.is_app_id_running', autospec=True)
def test_marathon_job_status(
    mock_is_app_id_running,
):
    mock_is_app_id_running.return_value = True

    app = mock.create_autospec(marathon.models.app.MarathonApp)
    app.tasks_running = 5
    app.deployments = []

    client = mock.create_autospec(marathon.MarathonClient)
    client.get_app.return_value = app

    job_config = mock.create_autospec(marathon_tools.MarathonServiceConfig)
    job_config.format_marathon_app_dict.return_value = {'id': 'mock_app_id'}
    job_config.get_instances.return_value = 5

    mstatus = marathon_job_status(client, job_config)
    print mstatus
    assert mstatus['status'] == 'Healthy'
