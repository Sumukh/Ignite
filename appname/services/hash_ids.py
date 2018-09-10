from hashids import Hashids

class HashIds:
    def init_app(self, app):
        salt = app.config.get('SECRET_KEY', 'appname-hashids-secret')
        self.hashids = Hashids(min_length=5, salt=salt)

    def encode_id(self, id_number):
        return self.hashids.encode(id_number)

    def decode_id(self, value):
        numbers = self.hashids.decode(value)
        if len(numbers) != 1:
            raise ValueError('Could not decode hash {0} into ID'.format(value))
        return numbers[0]
