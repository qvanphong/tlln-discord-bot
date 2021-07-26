import json
import definition


class ChannelPermission:
    channels = None

    def __init__(self):
        f = open(definition.get_path("assets/permission.json"), "r", encoding="utf8")
        self.channels = json.load(f)
        f.close()

    def can_use_command(self, channel_id, command):
        channel_id_str = str(channel_id)

        if channel_id_str in self.channels:
            permissions = self.channels[channel_id_str]
        else:
            permissions = self.channels["all"]

        allows = permissions["allow"]
        not_allows = permissions["not_allow"]

        # Only allow command excecute if that command in "allow" array (include 'all' commands)
        # and not in "not_allow" array
        # If that command not exist in passed server id, check the "all" permission
        if command in allows \
                or ("all" in allows and command not in not_allows) \
                or (command not in allows and command not in not_allows and command in self.channels["all"]["allow"]):
            return True
        else:
            return False
