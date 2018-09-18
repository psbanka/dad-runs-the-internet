# dad-runs-the-internet

## Overview

I'm a dad, so that's why I named this project what I named it. I have kids with
iPads and iPods and PCs, and while they're great kids who are smart and
conscientious and kind, sometimes I think that they spend too much time online
and that they lack self-control when it comes to using online services.
Sometimes they distance themselves from the family by constantly checking
Facebook or reddit. So this project puts control in your hands as a ~~dad~~
parent of kids with internet-connected devices.

The notion is that half of the code in this system runs on your wifi router.
This is meant to be used on a [ddwrt](http://www.dd-wrt.com/site/index) router
that has python and iptables support. This code frequently checks with a
website for rules to implement. It also reports up to the website any and all
MAC addresses that it sees connected to it. The notion here is that the
access-point is open and by default allows people through, then you, as an
administrator, log in to the website, decide what devices connected to your
network are what, and assign basic policies to them:

* No internet access
* Full internet access
* Permission-based access

The permission-based access nodes get access to the Internet for thirty (30)
minutes at a time. The idea here is that your kids say, "I'd like to use the
Internet for a while." and you, as a parent say, "Cool, I know you've done your
homework and have gotten lots of exercise today, so go ahead and use it for
half an hour." Then you pull out your smartphone, navigate to a web address you
have bookmarked, and find your son or daughter's device in the list, and tap
"grant permission."  The kid then has open access for that amount of time. 

Should your child want more access after their time is up, they have to ask you
again.  It makes sure that you all understand how much time is being used and
that they are spending their time wisely.

## How the hell does this thing work?


### Set up firebase

Set up a new firebase database. Configure it for very liberal ("testing") permissions.
Seed the data with the following:

```
curl -X PUT -d '{"iptables_download":{"allowed":[{"ip_address":"12.2.3.2"}],"blocked":[{"ip_address":"8.8.8.8"}]},"policies":{"message":{"upon_request":{"time":[".*.nist.gov",".*.pool.ntp.org"],"google":[".*.google.com","ssl.gstatic.com"],"dri":[".*amazonaws.com","freezing-frost-9935.herokuapp.com","ar.herokuapp.com",".*.googleapis.com"],"lastpass":[".*.lastpass.com"],"dev":[".*.atlassian.net"],"weather":[".*.accuweather.com"],"learning":[".*.dictionary.com",".*.wikipedia.org"],"evernote":[".*.evernote.com"],"mapping":[".*gpsonextra.net"],"podcasts":[".*.feedburner.net"]}}}}' https://lifesaver-15732.firebaseio.com/rules.json
```

### Set up the router
The router is the code that runs on the router.

do `python2 setup.py install`. that creates a `build/scripts-2.7/dri_daemon` file. 

Fire that thing up:

`python2 build/scripts/dri_daemon`

Go to your router, and configure dnsmasq properly:

~[screenshot](https://cl.ly/b609f4681fb4/%255B00b1a56e1ea3883ed2a4303dfed54eef%255D_Image%2525202018-09-09%252520at%25252014.37.27.png)


