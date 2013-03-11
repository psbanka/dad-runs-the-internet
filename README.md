dad-runs-the-internet
=====================

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
