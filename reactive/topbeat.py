from charms.reactive import when
from charms.reactive import when_file_changed
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import service_restart
from charmhelpers.fetch import apt_install

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index


@when('beat.repo.available')
@when_not('topbeat.installed')
def install_topbeat():
    status_set('maintenance', 'Installing topbeat')
    apt_install(['topbeat'], fatal=True)
    set_state('topbeat.installed')
    set_state('beat.render')


@when('beat.render')
def render_topbeat_template():
    render_without_context('topbeat.yml', '/etc/topbeat/topbeat.yml')
    remove_state('beat.render')
    status_set('active', 'Topbeat ready')


@when('config.changed.install_sources')
@when('config.changed.install_keys')
def reinstall_topbeat():
    remove_state('topbeat.installed')


@when_file_changed('/etc/topbeat/topbeat.yml')
def restart_topbeat():
    ''' Anytime we touch the config file, cycle the service'''
    service_restart('topbeat')


@when('topbeat.installed')
@when_not('topbeat.autostarted')
def enlist_topbeat():
    enable_beat_on_boot('topbeat')
    set_state('topbeat.autostarted')


@when('elasticsearch.available')
@when_not('topbeat.index.pushed')
def push_topbeat_index():
    push_beat_index('topbeat')
    set_state('topbeat.index.pushed')
