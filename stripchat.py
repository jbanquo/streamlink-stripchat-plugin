import re
import uuid
import requests

from streamlink.plugin import Plugin
from streamlink.plugin.plugin import parse_url_params
from streamlink.plugin.api import http
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream
from streamlink.utils import update_scheme

_url_re = re.compile(r"https?://(\w+\.)?stripchat\.com/(?P<username>\w+)")
_hls_url_re = re.compile(r"(hls(?:variant)?://)?(.+(?:\.m3u8)?.*)")

class Stripchat(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("username")

        # source: https://github.com/Damianonymous/StripchatRecorder/blob/main/StripchatRecorder.py
        resp = requests.get(f'https://stripchat.com/api/front/v2/models/username/{username}/cam').json()
        
        if 'cam' in resp.keys():
                if {'isCamAvailable', 'streamName', 'viewServers'} <= resp['cam'].keys():
                    if 'flashphoner-hls' in resp['cam']['viewServers'].keys():
                        hls_url = f'https://b-{resp["cam"]["viewServers"]["flashphoner-hls"]}.doppiocdn.com/hls/{resp["cam"]["streamName"]}/{resp["cam"]["streamName"]}.m3u8'
                        self.logger.info("HLS URL: {0}".format(hls_url))
                        HLSStream.parse_variant_playlist(self.session, hls_url)

                        # source: hls plugin
                        url, params = parse_url_params(hls_url)
                        urlnoproto = _hls_url_re.match(url).group(2)
                        urlnoproto = update_scheme("http://", urlnoproto)

                        self.logger.debug("URL={0}; params={1}", urlnoproto, params)
                        streams = HLSStream.parse_variant_playlist(self.session, urlnoproto, **params)
                        if not streams:
                            return {"live": HLSStream(self.session, urlnoproto, **params)}
                        else:
                            return streams


__plugin__ = Stripchat
