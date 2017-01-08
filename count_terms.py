
import json

from collections import defaultdict
from boltons.jsonutils import JSONLIterator
from boltons.dictutils import OMD
from lxml.html import soupparser


BRIEFINGS_FILE = 'briefings.jsonl'
CITIES_FILE = 'cities.json'

def main():
    cities_json = json.load(open(CITIES_FILE))
    pop_cities = sorted(cities_json, lambda o, _: int(o['population']), reverse=True)
    # print pop_cities[:20]
    cities = [o['city'] for o in pop_cities][:20]
    jsonl_iter = JSONLIterator(open(BRIEFINGS_FILE))

    res = defaultdict(list)

    for obj in jsonl_iter:
        title = obj['title']
        briefing_html = obj['content']

        content_tree = soupparser.fromstring(briefing_html)
        pane_tree = content_tree.cssselect('.pane-node-field-forall-body')
        briefing_text = pane_tree[0].text_content()

        for city in cities:
            if city in briefing_text:
                res[city].append(title)
                print 'found', repr(city), 'in', repr(title)

    omd = OMD()
    for k in res:
        omd.addlist(k, res[k])
    top_items = sorted(omd.counts().items(), key=lambda x: x[1], reverse=True)

    import pdb;pdb.set_trace()



if __name__ == '__main__':
    main()
