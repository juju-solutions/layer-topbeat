# Topbeat

A lightweight way to gather CPU, memory, and other per-process and system wide
data, then ship it to Elasticsearch to analyze the results.


## Usage

Topbeat can be added to any principal charm thanks to the wonders of being
a subordinate charm. The following usage example will deploy an ubuntu
metric source along with the elk stack so we can visualize our data.

    juju deploy ~containers/bundle/elk-stack
    juju deploy ~containers/topbeat
    juju deploy ubuntu
    juju add-relation topbeat:beats-host ubuntu
    juju add-relation topbeat logstash


### Deploying the minimal Beats formation

If you do not need log buffering and alternate transforms on data that is
being shipped to ElasticSearch, you can simply deploy the 'beats-core' bundle
which stands up Elasticsearch, Kibana, and the known working Beats
subordinate applications.

    juju deploy ~containers/bundle/beats-core
    juju deploy ubuntu
    juju add-relation filebeat:beats-host ubuntu
    juju add-relation topbeat:beats-host ubuntu

### Changing what is shipped

By default, the Topbeat charm is setup to ship everything:

    procs: .*

This is a regular expression to match the processes that are monitored

    juju config topbeat procs="^$"

would tell topbeat not to send any process data and only collect the machine
statistics such as load, ram, and disk usage.


## Testing the deployment

The applications provide extended status reporting to indicate when they are
ready:

    juju status

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch juju status

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can navigate to the kibana
url and view the streamed data from the Ubuntu host.

    juju status kibana --format=yaml | grep public-address

Navigate to http://&lt;kibana-ip&gt;/ in a browser and begin creating your
dashboard visualizations.


## Scale Out Usage with different configuration

Perhaps you want to monitor things slightly differently on only a few charms
in your model:

    juju deploy ~containers/topbeat custom-topbeat
    juju add-relation custom-topbeat:elasticsearch elasticsearch

You are then free to configure and relate custom-topbeat to your host(s) to be
monitored using the existing beats-core infrastructure you stood up in the
earlier example.


## Contact information

- Charles Butler <Chuck@dasroot.net>
- Matthew Bruzek <mbruzek@ubuntu.com>
- Tim Van Steenburgh <tim.van.steenburgh@canonical.com>
- George Kraft <george.kraft@canonical.com>
- Rye Terrell <rye.terrell@canonical.com>
- Konstantinos Tsakalozos <kos.tsakalozos@canonical.com>


# Need Help?

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju Community](https://jujucharms.com/community)
