import xml.etree.ElementTree as ET
from collections import defaultdict

class XmlReader:
    """
    XML parser using ElementTree object adding limit and filter options
    See https://stackoverflow.com/a/42193997/3456290
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.cache = defaultdict(list)
        self.root = None
        
    def reset_doc(self, filename):
        self.doc = ET.iterparse(filename, events=('start', 'end'))
        _, self.root = next(self.doc)

    def root_tag(self):
        if self.root is None:
            self.reset_doc(self.filename)
        return self.root.tag
    
    def count_tags(self, limit=None, filter_tags=None):
        tags = defaultdict(int)
        tags[self.root_tag()] = 1
        for e in self.iterate(limit=limit, filter_tags=filter_tags):
            tags[e.tag] += 1
            for ee in e.getchildren():
                tags[ee.tag] += 1
        return tags

    def unique_users(self, limit=None, filter_tags=None):
        users = set()
        for e in self.iterate(limit=limit, filter_tags=filter_tags):
            if 'uid' in e.attrib:
                users.add(e.attrib['uid'])
        return users
    
    def iterate(self, limit=None, filter_tags=None, use_cache=True):
        """
        Parse XML file allowing to use limit and filter optimising performance
        
        Args:
            limit(int): Limit of nodes to yield
            filter_tag(string): Tag name to apply as a filte
        """
        if use_cache and len(self.cache[(filter_tags, limit)]) > 0:
            for e in self.cache[(filter_tags, limit)]:
                yield e
            return True
        self.reset_doc(self.filename)
        count = 0
        start_tag = None
        for event, element in self.doc:
            if limit is not None:
                if count == limit:
                    return True
            if event == 'start' and start_tag is None:
                if filter_tags is None or (filter_tags is not None and element.tag in filter_tags):
                    start_tag = element.tag
            if event == 'end' and element.tag == start_tag:
                if use_cache:
                    self.cache[(filter_tags, limit)].append(element)
                yield element
                count += 1
                start_tag = None
                self.root.clear()
    
    def write_sample_file(self, n_skip=1000, filter_tags=('node', 'way', 'relation')):
        basename = self.filename.split('.')[0]
        filename = '%s_sample_%d.osm' % (basename, n_skip)
        with open(filename, 'wb') as output:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode())
            output.write('<osm>\n  '.encode())

            # Write every kth top level element
            for i, element in enumerate(self.iterate(filter_tags=filter_tags)):
                if i % n_skip == 0:
                    output.write(ET.tostring(element, encoding='utf-8'))

            output.write('</osm>'.encode())
