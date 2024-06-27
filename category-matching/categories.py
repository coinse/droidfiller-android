primary_category_BoW = {
    # functional categories (for general apps)
    'search': ['search', 'find', 'pattern'],
    'code': ['card', 'id', 'code', 'coupon'],
    'auth_code': ['auth', 'confirmation', 'verify', 'sms', 'email', 'code'],
    'label': ['label', 'title'],
    'description': ['description', 'content', 'notes', 'comment'],
    'tag': ['tag'],
    'profile': ['person', 'email', 'phone', 'password', 'username', 'country', 'countrycode', 'organization'],
    'datetime': ['date', 'time', 'year', 'month'],
    'location': ['location', 'region', 'city', 'country'],
    'numerical': ['ratio', 'rate', 'percentage', 'amount', 'count', 'balance', 'gram', 'enum', 'number'],

    # domain-specific categories (for target apps from specific domains)
    'ledger': ['balance', 'payee', 'account'],
    'device_profile': ['model', 'serial', 'number'],
    'music': ['song', 'artist', 'album', 'genre', 'music'],
    'messenger': ['conversation', 'message', 'chat', 'messenger']
}

secondary_category_BoW = {
    # functional categories
    'search': {
        'tv_show': ['show', 'tv', 'series'],
        'web': ['address', 'url', 'web'],
        'movie': ['movie', 'film'],
        'podcast': ['podcast', 'feed'],
        'car_model': ['car', 'model', 'series'],
        'location': ['location', 'where', 'place'],
        'megazine': ['megazine'],
        'music': ['music', 'song'],
        'video': ['video'],
        'manga': ['manga'],
        'news': ['news'],
        'book': ['book'],
        'country': ['country'],
        'country_code': ['country', 'code'],
        'app': ['appstore', 'app', 'game'],
        'iot_device': ['device', 'brand'],
        'storage': ['file', 'document', 'storage', 'library']
    },
    'code': {
        'card_id': ['card', 'id', 'barcode'],
        'coupon_code': ['coupon', 'code'],
    },
    'device_profile': {
        'model_name': ['model'],
        'serial_number': ['serial', 'number'],
    },
    'profile': {
        'age': ['age'],
        'country': ['country', 'nation'],
        'country_code': ['countrycode', 'cc'],
        'email': ['email'],
        'name': ['name', 'lastname', 'firstname', 'fullname'],
        'password': ['password'],
        'phone': ['phone', 'mobile', 'phonenumber'],
        'url': ['url', 'http', 'https'],
        'username': ['username', 'user', 'userid', 'nickname'],
        'job': ['job', 'organization'],
        'company': ['company'],
        'department': ['department'],
        'samsung_account': ['samsung', 'account'],
    },
    'location': {
        'city': ['city'],
        'country': ['country'],
        'location': ['location']
    },
    'datetime': {
        'year': ['year'],
        'month': ['month'],
        'hour': ['hour'],
        'minute': ['minute'],
        'second': ['second'],
        'date': ['date'],
        'time': ['time']
    },
    'numerical': {
        'amount': ['amount', 'count', 'balance', 'gram'],
        'ratio': ['ratio', 'rate', 'percentage'],
        'enum': ['enum', 'number'],
    },

    # domain-specific categories
    'ledger': {
        'payee': ['payee'],
        'balance': ['balance']
    },
    'music': {
        'artist': ['artist'],
        'album': ['album'],
        'song': ['song'],
        'genre': ['genre'],
        'playlist_url': ['playlist', 'url', 'youtube'],
        'number': ['number']
    },
    'messenger': {
        'recipient': ['recipient'],
        'message': ['message', 'conversation'],
    }
}


secondary_category_BoW_flattened = {}
for primary_category, secondary_category_dict in secondary_category_BoW.items():
    for secondary_category, tokens in secondary_category_dict.items():
        secondary_category_BoW_flattened[secondary_category] = tokens
