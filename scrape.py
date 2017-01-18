
import json
import urllib2
import datetime

from lxml.html import soupparser
from boltons.iterutils import chunked

BASE_URL = 'https://www.whitehouse.gov'
BASE_IDX_URL = 'https://www.whitehouse.gov/briefing-room/press-briefings?term_node_tid_depth=36&page='


def get_url(url):
    print 'fetching url:', url
    return urllib2.urlopen(url).read()


def qualify_url(url):
    if not url:
        return url
    if not url.startswith('http'):
        return BASE_URL + url
    return url


def get_briefing_links(idx=0):
    resp_bytes = get_url(BASE_IDX_URL + str(idx))
    resp_tree = soupparser.fromstring(resp_bytes)

    items = resp_tree.cssselect('div.views-row .field-content')
    date_link_elems = chunked(items, 2)

    ret = [(date.text_content(),
            link.text_content(),
            qualify_url(link.find('a').get('href')))
           for date, link in date_link_elems]
    return ret


def write_json_line(path, obj):
    with open(path, 'ab') as f:
        obj_bytes = json.dumps(obj, sort_keys=True)
        f.write(obj_bytes)
        f.write('\n')
    return


def main():
    total_scraped = 0
    for i in range(178):
        print 'getting links for page', i
        cur_links = get_briefing_links(i)
        if not cur_links:
            return
        print 'got', len(cur_links), 'links'
        for date, title, url in cur_links:
            cur_resp_bytes = get_url(url)
            obj = {'url': url,
                   'date': date,
                   'title': title,
                   'page_index': i,
                   'content': cur_resp_bytes,
                   'datetime': datetime.datetime.utcnow().isoformat()}
            print 'writing json line for', repr(title)
            write_json_line('briefings.jsonl', obj)
            total_scraped += 1
            print ' -- total scraped:', total_scraped
    return


if __name__ == '__main__':
    main()
