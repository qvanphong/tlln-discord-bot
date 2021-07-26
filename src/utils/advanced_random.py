from src.model.random_model import AdvancedRandomModel
import random


def get_random_number(minimum, maximum):
    return random.randint(int(minimum), int(maximum))


class AdvancedRandom:
    random_sessions = []

    def get_random_with_exclude(self, author):
        index = self.get_author_index(author)
        if index != -1:
            random_model = self.random_sessions[index]

            while True:
                if random_model.maximum == len(random_model.exclude):
                    return ["Không còn số để quay.", random_model.exclude]
                random_number = random.randint(random_model.minimum, random_model.maximum)
                if random_number not in random_model.exclude:
                    random_model.exclude.append(random_number)
                    return [random_number, random_model.exclude]

    def get_author_index(self, author):
        for index, random_model in enumerate(self.random_sessions):
            if random_model.owner.id == author.id:
                return index
        return -1

    def add_random_session(self, minimum, maximum, channel_id, author):
        index = self.get_author_index(author)
        if index == -1:
            random_model = AdvancedRandomModel(minimum=int(minimum),
                                               maximum=int(maximum),
                                               owner=author,
                                               channel_id=channel_id)
            self.random_sessions.append(random_model)
        else:
            self.random_sessions[index] = AdvancedRandomModel(minimum=int(minimum),
                                                              maximum=int(maximum),
                                                              owner=author,
                                                              channel_id=channel_id)

    def remove_random_session(self, author):
        index = self.get_author_index(author)
        if index != -1:
            self.random_sessions.pop(index)
            return True
        return False
