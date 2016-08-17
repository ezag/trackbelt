from urllib import urlencode
from urlparse import parse_qs, urlparse

class VkPermission(object):
    AUDIO = 8
    
if __name__ == '__main__':
    url = 'https://oauth.vk.com/authorize'
    uid = None
    query = urlencode(dict(
        client_id=4301930,
        redirect_uri='https://oauth.vk.com/blank.html',
        display='page',
        scope=VkPermission.AUDIO,
        response_type='token',
    ))
    print "{}?{}".format(url, query)
    print ">",
    redirect_url = raw_input()
    access_token = parse_qs(urlparse(redirect_url).fragment)['access_token'][0]
    query = 'https://api.vk.com/method/audio.get?{}'.format(urlencode(dict(
        access_token=access_token,
        owner_id=uid,
    )))
    print query
