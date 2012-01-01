from dojango import forms

POLICY_CHOICES = (
    ('full', 'Full Internet Access all the time'),
    ('upon-request', 'Device can access Internet when approved'),
    ('blocked', 'Device has no access to the Internet'),
)

SYSTEM_CHOICES = (
    ('windows', 'Windows-based PC or laptop'),
    ('macintosh', 'Apple Macintosh desktop or laptop'),
    ('ipod', 'Apple iPod'),
    ('iphone', 'Apple iPhone'),
    ('android', 'Google Android phone'),
    ('ipad', 'Apple iPad'),
    ('xbox', 'Microsoft XBox'),
    ('ps/3', 'Sony Playstation/3'),
    ('other', 'Another type of device'),
)

class DeviceForm(forms.Form):

    mac_address = forms.CharField(
        required=True, 
        widget=forms.HiddenInput())

    device_name = forms.CharField(
        required=True, 
        #help_text="Jeremy's iPod",  # Doesn't work at current -pbanka
        widget=forms.TextInput())

    policy = forms.ChoiceField(
        choices=POLICY_CHOICES,
        required=True,
        widget=forms.Select)

    device_type = forms.ChoiceField(
        choices=SYSTEM_CHOICES,
        required=False,
        widget=forms.Select)

