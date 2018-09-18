{
  "iptables_download": {
    "allowed": [
      {
        "ip_address": "12.2.3.2"
      }
    ],
    "blocked": [
      {
        "ip_address": "8.8.8.8"
      }
    ]
  },
  "policies": {
    "message": {
      "upon_request": {
        "time": [".*.nist.gov", ".*.pool.ntp.org",],
        "google": [".*.google.com", "ssl.gstatic.com",],
        "dri": [ ".*amazonaws.com", "freezing-frost-9935.herokuapp.com", "ar.herokuapp.com", ".*.googleapis.com",],
        "lastpass": [".*.lastpass.com",],
        "dev": [".*.atlassian.net",],
        "weather": [ ".*.accuweather.com",],
        "learning": [".*.dictionary.com", ".*.wikipedia.org",],
        "evernote": [".*.evernote.com",],
        "mapping": [".*gpsonextra.net",],
        "podcasts": [".*.feedburner.net",],
      }
    }
  }
}
curl -X PUT -d '{"iptables_download":{"allowed":[{"ip_address":"12.2.3.2"}],"blocked":[{"ip_address":"8.8.8.8"}]},"policies":{"message":{"upon_request":{"time":[".*.nist.gov",".*.pool.ntp.org"],"google":[".*.google.com","ssl.gstatic.com"],"dri":[".*amazonaws.com","freezing-frost-9935.herokuapp.com","ar.herokuapp.com",".*.googleapis.com"],"lastpass":[".*.lastpass.com"],"dev":[".*.atlassian.net"],"weather":[".*.accuweather.com"],"learning":[".*.dictionary.com",".*.wikipedia.org"],"evernote":[".*.evernote.com"],"mapping":[".*gpsonextra.net"],"podcasts":[".*.feedburner.net"]}}}}' https://lifesaver-15732.firebaseio.com/rules.json
