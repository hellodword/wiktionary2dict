from wikitextparser import WikiText
from xml.dom.minidom import Element
from xml.dom import pulldom
from typing import Callable, Tuple
import bz2


class BZ2OrXml(object):
    def __init__(self, filename):
        if filename.endswith('.bz2'):
            self.file = bz2.BZ2File(filename)
        else:
            self.file = open(filename)

    def __enter__(self):
        return self.file

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.file.close()


def getElementTextByTagName(node: Element, name: str) -> str | None:
    elements = node.getElementsByTagName(name)
    if elements.length == 0:
        return None
    if not elements[0].hasChildNodes():
        return None
    return elements[0].firstChild.wholeText


def parse_wiktionary(
    path: str,
    redirect_cb: Callable[[str, str], any] = None,
    wikitext_cb: Callable[[str, WikiText], any] = None,
):

    def redirect_handle(title: str, redirect: str):
        if redirect_cb is not None:
            redirect_cb(title, redirect)
        return None

    def wikitext_handle(title: str, text: str):
        if title is None:
            return None
        if text is None:
            return None

        w = WikiText(text)
        if w is None:
            return None

        if wikitext_cb is not None:
            wikitext_cb(title, w)

    def page_handle(node: Element) -> Tuple[str | None, str | None, str | WikiText | None]:
        redirects = node.getElementsByTagName('redirect')
        if redirects.length > 0:
            return redirect_handle(
                getElementTextByTagName(node, 'title'),
                redirects[0].getAttribute('title'),
            )

        model = getElementTextByTagName(node, 'model')
        if model == 'wikitext':
            return wikitext_handle(
                getElementTextByTagName(node, 'title'),
                getElementTextByTagName(node, 'text'),
            )
        return model, getElementTextByTagName(node, 'title'), None

    with BZ2OrXml(path) as f:
        events = pulldom.parse(f)

        for (event, node) in events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'page':
                    events.expandNode(node)
                    page_handle(node)


class Wiktionary2Dict:

    @staticmethod
    def run():

        def wikitext_cb(title: str, w: WikiText):
            if title == 'free':
                print('span', w.span)
                print('parameters', w.parameters)
                print('comments', w.comments)
                print('external_links', w.external_links)
                print('wikilinks', w.wikilinks)
                print('parser_functions', w.parser_functions)
                print('tables', w.tables)
                print('_extension_tags', w._extension_tags)
                # print('sections', w.sections)
                # print('templates', w.templates)

        parse_wiktionary('./data/en.sample.xml.bz2', wikitext_cb=wikitext_cb)

        from .skywind3000.writemdict.writemdict import MDictWriter

        dictionary = {"doe": "a deer, a female deer.",
                      "ray": "a drop of golden sun.",
                      "me": "a name I call myself.",
                      "far": "a long, long way to run."}

        writer = MDictWriter(dictionary,
                             title="Example Dictionary",
                             description="This is an example dictionary.",
                             compression_type=0)
        with open('./data/sample.mdx', 'wb') as f:
            writer.write(f)
        with open('./data/sample.mdx.header', 'wb') as f:
            writer._write_header(f)
        with open('./data/sample.mdx.key', 'wb') as f:
            writer._write_key_sect(f)
        with open('./data/sample.mdx.record', 'wb') as f:
            writer._write_record_sect(f)
