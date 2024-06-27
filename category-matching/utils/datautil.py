import os
import typing
import json
import xmltodict
import xml.etree.ElementTree as et

def json_obj_to_xml(parent_element: typing.Optional[et.Element], new_element_name: str, obj: typing.Union[bool, float, int, str, dict, list]):
    """
    Recursively walk an object and return its XML representation.

    Args:
        parent_element (typing.Optional[et.Element]): The element that will be the parent of the element that this
            function will create and return.

        new_element_name (str): The name of the element that will be created.

        obj (typing.Union[bool, float, int, str, dict, list]): The object to return XML for.  It is expected that all
            objects passed to this function can be represented in JSON.

    Returns:
        result (et.Element): An XML element.

    """

    if parent_element is not None:
        new_element = et.SubElement(parent_element, new_element_name)

    else:
        new_element = et.Element(new_element_name)

    if type(obj) == dict:
        for key, value in obj.items():
            if key == "children":
                assert type(value) == list
                for child_elem in value:
                    json_obj_to_xml(new_element, child_elem['class_'], child_elem)
            elif key == "ancestors":
                pass
            else:
                # Convert values to a string, make sure boolean values are lowercase
                if key == "class_":
                    new_key = "class"
                else:
                    new_key = key
                new_element.attrib[new_key] = str(value).lower() if type(value) == bool else str(value)

    elif type(obj) == list:
        for list_item in obj:
            # List items have to have a name.  Here we borrow "li" from HTML which stands for list item.
            json_obj_to_xml(new_element, 'li', list_item)

    else:
        # Convert everything to a string, make sure boolean values are lowercase
        new_element.text = str(obj).lower() if type(obj) == bool else str(obj)

    return new_element


def xml_to_dict(root_xml_element):
    return xmltodict.parse((et.tostring(root_xml_element)))


def get_textfields(view_tree):
    textfields = view_tree.findall('.//android.widget.EditText')
    textfields.extend(view_tree.findall('.//android.widget.AutoCompleteTextView'))
    textfields.extend(view_tree.findall('.//android.widget.ExtractEditText'))
    textfields_list = []

    for e in textfields:
        tf = e.attrib.copy()
        tf['type'] = 'textfield'

        textfields_list.append(tf)

    return textfields_list
