from charms.reactive import when
from charms.reactive import when_any
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state
from charms.reactive import hook
import charms.apt

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import service_restart, service_stop

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index

import os


@when_not('apt.installed.topbeat')
def install_topbeat():
    status_set('maintenance', 'Installing topbeat.')
    charms.apt.queue_install(['topbeat'])
    set_state('topbeat.installed')
    set_state('beat.render')


@when('beat.render')
@when_any('elasticsearch.available', 'logstash.available', 'kafka.ready')
def render_topbeat_template():
    render_without_context('topbeat.yml', '/etc/topbeat/topbeat.yml')
    remove_state('beat.render')
    status_set('active', 'Topbeat ready.')
    service_restart('topbeat')


@when('config.changed.install_sources')
@when('config.changed.install_keys')
def reinstall_topbeat():
    remove_state('apt.installed.topbeat')


@when('apt.installed.topbeat')
@when_not('topbeat.autostarted')
def enlist_topbeat():
    enable_beat_on_boot('topbeat')
    set_state('topbeat.autostarted')


@when('apt.installed.topbeat')
@when('elasticsearch.available')
@when_not('topbeat.index.pushed')
def push_topbeat_index(elasticsearch):
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
    push_beat_index(host_string, 'topbeat')
    set_state('topbeat.index.pushed')


@hook('stop')
def remove_topbeat():
    service_stop('topbeat')
    try:
        os.remove('/etc/topbeat/topbeat.yml')
    except OSError:
        pass
    charms.apt.purge('topbeat')
