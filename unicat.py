from lxml import etree

class Book:
    def __init__(self, xml_string):
        self.doc = etree.fromstring(xml_string)
        self.ns = {
            "slim": "http://www.loc.gov/MARC21/slim",
            "srw": "http://www.loc.gov/zing/srw/",
            "xcql": "http://www.loc.gov/zing/cql/xcql/",
        }

    def xpath(self, xpath_str, element=None):
        """Convenience method"""
        if element is None:
            element = self.doc
        return element.xpath(xpath_str, namespaces=self.ns)

    def isbns(self):
        all_isbns = set()
        # concatentate results of multiple records, if present
        for isbn_string in self.xpath(
            '//slim:datafield[@tag="020"]/slim:subfield[@code="a"]/text()'
        ):
            all_isbns |= set(isbn_string.split())

        if not all_isbns:
            # ISBN not in Unicat. We can only give back the ISBN as it was looked up.
            all_isbns = {self.looked_up_isbn}
        return all_isbns
    
    @property
    def looked_up_isbn(self):
        return self.xpath("//xcql:searchClause/xcql:term/text()")[0]

    @property
    def raw_xml(self):
        return etree.tostring(self.doc)

    def holdings(self):
        # TODO figure out hwo to handle cases with more than one record!!
        # XML shouldn't contain more than one record
        multiple_records = 0
        if len(self.xpath("//slim:record")) > 1:
            multiple_records += 1
        for el in self.xpath('//slim:datafield[@tag="852"]'):
            location = self.xpath('slim:subfield[@code="a"]/text()', el)[0]
            uri = self.xpath('slim:subfield[@code="u"]/text()', el)[0]

            yield str(location), str(uri)
    
    def isbn_look_up(self):
        # this is a function added to look up the initial ISBN used for the search
        isbn = self.xpath(".//xcql:term/text()")[0]
        return isbn

    @property        
    def number_of_records(self):
        # The element srw:numberOfRecords reports 2 when there's 1, so is unreliable
        return len(self.xpath('//slim:record'))