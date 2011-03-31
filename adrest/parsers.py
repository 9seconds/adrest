from django.utils import simplejson as json

from adrest import status
from adrest.utils import HttpError


class ParserMixin(object):

    parsers = tuple()

    def parse(self, content_type):

        split = content_type.split(';', 1)
        if len(split) > 1:
            content_type = split[0]
        content_type = content_type.strip()

        media_type_to_parser = dict([(parser.media_type, parser) for parser in self.parsers])

        try:
            parser = media_type_to_parser[content_type]
        except KeyError:
            parser = FormParser

        return parser(self).parse()


class BaseParser(object):
    media_type = None

    def __init__(self, resource):
        self.resource = resource

    def parse(self):
        return self.resource.request.raw_post_data


class JSONParser(BaseParser):
    media_type = 'application/json'

    def parse(self):
        try:
            return json.loads(self.resource.request.raw_post_data)
        except ValueError, e:
            raise HttpError('JSON parse error - %s' % str(e), status=status.HTTP_400_BAD_REQUEST)


class XMLParser(BaseParser):
    media_type = 'application/xml'


class FormParser(BaseParser):
    media_type = 'application/x-www-form-urlencoded'

    def parse(self):
        return dict(self.resource.request.REQUEST.iteritems())
