from enum import Enum


class XMLExeption(Exception):
    pass


class Profile(Enum):
    DEFAULT, CPU, SERVER = range(3)

    @staticmethod
    def from_str(profile):
        l_profile = profile.lower() if profile else None
        if l_profile == 'cpu':
            return Profile.CPU
        elif l_profile == 'server':
            return Profile.SERVER

        return Profile.DEFAULT


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def has(x):
    return x is not None


def get_text(node):
    if has(node):
        return node.text
    return None


def remove_elements(node, name):
    for found in node.iterfind(name):
        found.getparent().remove(found)
