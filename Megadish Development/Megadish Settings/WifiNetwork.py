import json

class WifiNetwork:
    def __init__(self, ssid, password, security_type, hidden=False, bssid=None,
                 encryption_type=None, frequency=None, channel=None, mode=None,
                 country_code=None, static_ip=None, dhcp=True, priority=0):
        self.ssid = ssid
        self.password = password
        self.security_type = security_type
        self.hidden = hidden
        self.bssid = bssid
        self.encryption_type = encryption_type
        self.frequency = frequency
        self.channel = channel
        self.mode = mode
        self.country_code = country_code
        self.static_ip = static_ip
        self.dhcp = dhcp
        self.priority = priority

    def to_dict(self):
        return {
            "ssid": self.ssid,
            "password": self.password,
            "security_type": self.security_type,
            "hidden": self.hidden,
            "bssid": self.bssid,
            "encryption_type": self.encryption_type,
            "frequency": self.frequency,
            "channel": self.channel,
            "mode": self.mode,
            "country_code": self.country_code,
            "static_ip": self.static_ip,
            "dhcp": self.dhcp,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["ssid"],
            data["password"],
            data["security_type"],
            data.get("hidden", False),
            data.get("bssid"),
            data.get("encryption_type"),
            data.get("frequency"),
            data.get("channel"),
            data.get("mode"),
            data.get("country_code"),
            data.get("static_ip"),
            data.get("dhcp", True),
            data.get("priority", 0)
        )


