from lxml import etree


class XMLParser:
    @staticmethod
    def get_element_name(elem, root):
        """
        Utility function to retrieve the direct name of an xml element "elem",
        given that a direct child with the tag name "name" exists in the xml tree
        ==============================================
        @:param elem: ElementTree - element to get name from
        @:param root: ElementTree - root of the xml tree (for retrieving the ns namespace map)
        @:returns elem_name: string - if <name> exists as a direct child of "elem"
                                     or None otherwise
        """
        elem_name = elem.findall('name', root.nsmap)
        if len(elem_name):
            return elem_name[0].text
        return None

    def parse_xml_file(self, filename):
        """
        Returns a dictionary representation of the class names and their corresponding comment
        and identifier lists for each class in "filename"
        ==============================================
        @:param filename: string - path to xml file representation of a project
        @:returns class_identifier_comments_dict: dict - dictionary of the form
        { class_name: { 'identifiers': [...], 'comments;: [...] }, where the list of
        identifiers, respectively comments are composed of strings
        """
        class_identifier_comments_dict = {}
        tree = etree.parse(filename)
        root = tree.getroot()
        for unit_elem in root.findall('.//unit', root.nsmap):
            comment_list_unit = [comment.text for comment in unit_elem.iterfind('.//comment', root.nsmap) if
                                 comment.text.find('Copyright') == -1]
            for class_elem in unit_elem.findall('class', root.nsmap):
                class_name = self.get_element_name(class_elem, root)
                class_identifier_comments_dict[class_name] = {}
                identifier_list = []
                for decl_stmt_elem in class_elem.iterfind('.//decl', root.nsmap):
                    attribute_name = self.get_element_name(decl_stmt_elem, root)
                    identifier_list.append(attribute_name)
                for function_elem in class_elem.iterfind('.//function', root.nsmap):
                    function_name = self.get_element_name(function_elem, root)
                    identifier_list.append(function_name)
                class_identifier_comments_dict[class_name]['identifiers'] = identifier_list
                class_identifier_comments_dict[class_name]['comments'] = comment_list_unit
        return class_identifier_comments_dict
