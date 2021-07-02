import json


class ChannelPermission():
    channels_permission = None

    def __init__(self):
        f = open("assets/permission.json", "r")
        self.channels_permission = json.load(f)
        f.close()

    def can_use_command(self, channel, command):
        if channel in self.channels_permission:
            channel_permissions = self.channels_permission[channel]
            allows = channel_permissions["allow"]
            not_allows = channel_permissions["not_allow"]

            if command in allows:
                return True
            if "all" in allows and command not in not_allows:
                return True
            else:
                return False
        else:
            return False

    def has_permission(self, channel):
        return channel in self.channels_permission
