---
layout: post
title: A simple init.d script template for use with Ansible

---

> Don't know anything about Ansible, and want to know why you might want to care?  Have a look at my [previous post](/2013/03/17/ansible.html).

# Feedback?
*Am I doing it wrong, or do you have ideas for improvement? Don't hesitate to drop me an [email](mailto:fredrik.dyrkell@gmail.com)! I'd love to learn more!*

<hr>

From an [Ansible](http://ansible.cc) [playbook](http://ansible.cc/docs/playbooks.html) you can make sure that a [service](http://ansible.cc/docs/modules.html#service) is running on a remote machine:

{% highlight yaml %}

- name: Ensure my daemon myd is started
  action: service name=myd state=started

{% endhighlight %}

This will basically run a status check

{% highlight bash %}
sudo service myd status
{% endhighlight %}

and if it's not already running

{% highlight bash %}
sudo service myd start
{% endhighlight %}

The exact underlying commands that Ansible will run depends on your system.

# But oh noes

This works out fine, for any application that already got the lifecycle scripts set up, such as for example Apache httpd. For my test application, made using [Twisted](http://twistedmatrix.com/trac/wiki), I'm not in such luck. 

The service command runs scripts either located in /etc/init or in /etc/init.d. We're going to create an init.d script that starts, stops and gives the current status of our Twisted daemon. 

# Template

The init.d script is created as a Ansible template. The template is written to be generic in the sense that it doesn't know what specific daemon it is starting or stopping. Instead it is using variables set in the playbook to specify 

- The path to the daemon to start
- Parameters to the daemon
- Path to the pidfile
- Name of the service 

{% highlight bash %}
{% raw %}
#!/bin/sh

SERVICE_NAME={{service_name}}
DAEMON={{daemon}}
DAEMON_OPTS="{{daemon_opts}}"
PIDFILE={{pidfile}}

if [ ! -x $DAEMON ]; then
  echo "ERROR: Can't execute $DAEMON."
  exit 1
fi

start_service() {
  echo -n " * Starting $SERVICE_NAME... "
  start-stop-daemon -Sq -p $PIDFILE -x $DAEMON -- $DAEMON_OPTS
  e=$?
  if [ $e -eq 1 ]; then
    echo "already running"
    return
  fi

  if [ $e -eq 255 ]; then
    echo "couldn't start :("
    exit 1
  fi

  echo "done"
}

stop_service() {
  echo -n " * Stopping $SERVICE_NAME... "
  start-stop-daemon -Kq -R 10 -p $PIDFILE
  e=$?
  if [ $e -eq 1 ]; then
    echo "not running"
    return
  fi

  echo "done"
}

status_service() {
    printf "%-50s" "Checking $SERVICE_NAME..."
    if [ -f $PIDFILE ]; then
        PID=`cat $PIDFILE`
        if [ -z "`ps axf | grep ${PID} | grep -v grep`" ]; then
            printf "%s\n" "Process dead but pidfile exists"
            exit 1 
        else
            echo "Running"
        fi
    else
        printf "%s\n" "Service not running"
        exit 3 
    fi
}

case "$1" in
  status)
    status_service
    ;;
  start)
    start_service
    ;;
  stop)
    stop_service
    ;;
  restart)
    stop_service
    start_service
    ;;
  *)
    echo "Usage: service $SERVICE_NAME {start|stop|restart|status}" >&2
    exit 1   
    ;;
esac

exit 0
{% endraw %}
{% endhighlight %}

# Gotchas

First, you might notice that I specify a pidfile when starting up the service (`start_service` function). The reason is that Twisted does create a pidfile for me. If your particular daemon doesn't provide you with that, you might want to try adding the option `--make-pidfile` to `start-stop-daemon`, when starting up. (Note that I haven't tried it, and that the documentation specificly mentions that it might not work for all cases.) 

Secondly, I ran into some debugging with regards to how Ansible interprets the scripts exit codes. The exit codes from start and stop do work the way you expect, but for the status options the expected return values are a bit different. [This page](http://refspecs.linuxbase.org/LSB_3.1.1/LSB-Core-generic/LSB-Core-generic/iniscrptact.html) had a nice table for the expected exit codes.

# `status` exit codes
- 0,    program is running or service is OK
- 1,    program is dead and /var/run pid file exists
- 2,    program is dead and /var/lock lock file exists
- 3,    program is not running
- 4,    program or service status is unknown

# Any other than `status`, (`start`|`stop` etc)
- 1,   generic or unspecified error (current practice)
- 2,   invalid or excess argument(s)
- 3,   unimplemented feature (for example, "reload")
- 4,   user had insufficient privilege
- 5,   program is not installed
- 6,   program is not configured
- 7,   program is not running

# Tiying it all together

We can now make sure our service is running by copying our template into the `/etc/init.d` folder and ensure the service is running. The example below shows the variables from my [Vagrant](http://www.vagrantup.com/) configuration installing the Twisted daemon.

{% highlight yaml %}
  vars:

    user: vagrant
    daemon: /home/vagrant/.virtualenvs/twisted/bin/twistd
    pidfile: /var/run/myd.pid
    daemon_opts: "-y /home/vagrant/app/myd.py --pidfile=/var/run/myd.pid --logfile=/var/log/myd.log"
    service_name: myd

  tasks:

  - name: Add twistd init.d daemon script
    action: template src=templates/init.d-template.j2 dest=/etc/init.d/myd mode=0751
  - name: Ensure my daemon myd is started
    action: service name=myd state=started

{% endhighlight %}
