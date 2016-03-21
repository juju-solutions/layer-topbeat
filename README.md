# Topbeat

A lightweight way to gather CPU, memory, and other per-process and system wide data, then ship it to Elasticsearch to analyze the results.

## Usage

Top can be added to any principal charm thanks to the wonders of being
a subordinate charm. You can simply deploy the 'beats-base' bundle
which stands up Elasticsearch, Kibana, and the three known working Beats
subordinate services.

    juju deploy ~containers/bundle/beats-core
    juju deploy ubuntu
    juju add-relation topbeat:beats-host ubuntu


### A note about the beats-host relationship

The Beats suite of charms leverage the implicit "juju-info" relation interface
which is special and unique in the context of subordinates. This is what allows
us to relate the beat to any host, but may have some display oddities in the
juju-gui. Until this is resolved, it's recommended to relate beats to their
principal services using the CLI

### Changing whats being shipped

by default, the Topbeat charm is setup to ship everything:

    procs: .*

This is a regular expression to match the processes that are monitored

    juju set topbeat procs="^$"

would tell topbeat not to send any process data and only collect the machine
statistics such as load, ram, and disk usage.


## Testing the deployment

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can navigate to the kibana
url and view the streamed log data from the Ubuntu host.

    juju status kibana --format=yaml | grep public-address

  open http://&lt;kibana-ip&gt;/ in a browser and begin creating your dashboard
  visualizations

## Scale Out Usage with different configuration

Perhaps you want to monitor things slightly differently on only a few charms
in your model:

    juju deploy ~containers/trusty/topbeat custom-topbeat
    juju add-relation custom-topbeat:elasticsearch elasticsearch

you are then free to relate this subordinate, and configure it for exactly
how you want the hosts to be monitored, using the existing beats-core infrastructure
you've stood up in the earlier example.



## Contact information

- Charles Butler &lt;charles.butler@canonical.com&gt;
- Matt Bruzek &lt;matthew.bruzek@canonical.com&gt;

# Need Help?

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju Community](https://jujucharms.com/community)
