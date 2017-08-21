import re
import json


class MapDocument:


    def __init__(self, element=None, jsondoc=None, street_auditor=None):
        self.street_auditor = street_auditor
        if element is not None:
            self.doc = self.parse_element(element)
        elif jsondoc is not None:
            self.doc = json.reads(jsondoc)

    def todict(self):
        return self.doc

    def parse_element(self, element):
        lower = re.compile(r'^([a-z]|_)*$')
        lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
        problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
        CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
        doc = {}
        if element.tag in ["node", "way"]:
            doc['type'] = element.tag
            for a in element.attrib:
                if a in CREATED:
                    if 'created' not in doc:
                        doc['created'] = {}
                    doc['created'][a] = element.attrib[a]
                elif a in ('lat','lon'):
                    if 'pos' not in doc:
                        doc['pos'] = [0,0]
                    key = 0 if a == 'lat' else 1
                    doc['pos'][key] = float(element.attrib[a])
                else:
                    doc[a] = element.attrib[a]
            for t in element.iter('tag'):
                if problemchars.search(t.attrib['k']):
                    continue
                elif t.attrib['k'].startswith('addr:') or t.attrib['k'] == 'address':
                    if 'address' not in doc:
                        doc['address'] = {}
                    if t.attrib['k'] == 'address':
                        doc['address']['unparsed'] = t.attrib['v']
                    elif t.attrib['k'].count(':') == 1:
                        addr_type = t.attrib['k'].split(':')[1]
                        if addr_type == 'street' and self.street_auditor is not None:
                            value = self.street_auditor.update_name(t.attrib['v'])
                        else:
                            value = t.attrib['v']
                        try:
                            doc['address'][addr_type] = value
                        except TypeError as e:
                            print(doc['address'], addr_type)
                else:
                    key = t.attrib['k'].replace(':', '_')
                    doc[key] = t.attrib['v']
            if element.tag == 'way':
                for t in element.iter('nd'):
                    if 'node_refs' not in doc:
                        doc['node_refs'] = []
                    if 'ref' in t.attrib:
                        doc['node_refs'].append(t.attrib['ref'])
            return doc
        return None
