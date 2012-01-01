from dojango import forms

POLICY_CHOICES = (
    ('full', 'Full Internet Access all the time'),
    ('upon-request', 'Device can access Internet when approved'),
    ('blocked', 'Device has no access to the Internet'),
)

class DeviceForm(forms.Form):

    device_name = forms.CharField(
        required=True, 
        #help_text="Jeremy's iPod", 
        widget=forms.TextInput())

    policy = forms.ChoiceField(
        choices=POLICY_CHOICES,
        required=True,
        widget=forms.Select)

