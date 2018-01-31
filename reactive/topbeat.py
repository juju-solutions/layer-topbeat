import charms.apt
from charms.reactive import when
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state
from charms.reactive import hook
from charms.templating.jinja2 import render

from charmhelpers.core.hookenv import config, status_set
from charmhelpers.core.host import restart_on_change, service_stop

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index

import base64
import os


LOGSTASH_SSL_CERT = '/etc/ssl/certs/topbeat-logstash.crt'
LOGSTASH_SSL_KEY = '/etc/ssl/private/topbeat-logstash.key'


@when_not('apt.installed.topbeat')
def install_topbeat():
    status_set('maintenance', 'Installing topbeat.')
    charms.apt.queue_install(['topbeat'])


@when('beat.render')
@when('apt.installed.topbeat')
@restart_on_change({
    '/etc/topbeat/topbeat.yml': ['topbeat']
    })
def render_topbeat_template():
    connections = render_without_context('topbeat.yml', '/etc/topbeat/topbeat.yml')
    remove_state('beat.render')
    if connections:
        status_set('active', 'Topbeat ready.')


@when('beat.render')
@when('apt.installed.topbeat')
@restart_on_change({
    LOGSTASH_SSL_CERT: ['topbeat'],
    LOGSTASH_SSL_KEY: ['topbeat'],
    })
def render_topbeat_logstash_ssl_cert():
    logstash_ssl_cert = config().get('logstash_ssl_cert')
    logstash_ssl_key = config().get('logstash_ssl_key')
    if logstash_ssl_cert and logstash_ssl_key:
        render(template='{{ data }}',
               context={'data': base64.b64decode(logstash_ssl_cert)},
               target=LOGSTASH_SSL_CERT, perms=0o444)
        render(template='{{ data }}',
               context={'data': base64.b64decode(logstash_ssl_key)},
               target=LOGSTASH_SSL_KEY, perms=0o400)
    else:
        if not logstash_ssl_cert and os.path.exists(LOGSTASH_SSL_CERT):
            os.remove(LOGSTASH_SSL_CERT)
        if not logstash_ssl_key and os.path.exists(LOGSTASH_SSL_KEY):
            os.remove(LOGSTASH_SSL_KEY)


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
