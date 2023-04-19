import datetime
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
            if title in ['a', 'of', 'to', 'in', 'for', 'have', 'you', 'let', 'make', 'get', 'free', 'idiom', 'the', 'be', 'and']:
                print('title', title)
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

        # parse_wiktionary('./data/en.sample.xml.bz2', wikitext_cb=wikitext_cb)

        dictionary = {
            "doe": "a deer, a female deer.",
            "0ray": "a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. a drop of golden sun. ",
            "far": "a long, long way to run.",
            "me": "中文 麵麪麵 .",
            "far2": "a long, long way to run.",
        }

        from mdict_utils.base.writemdict import MDictWriter
        from .writemdict.writemdict import MDictWriter as MDictWriterStream

        # writer = MDictWriter(
        #     title="Example Dictionary",
        #     description="This is an example dictionary.",
        #     compression_type=2,
        #     is_mdd=False,
        # )

        # writer._build_offset_table(dictionary)
        # writer._build_key_blocks()
        # writer._build_keyb_index()
        # writer._build_record_blocks()
        # writer._build_recordb_index()
        # with open('./data/sample.mdx', 'wb') as f:
        #     writer.write(f)

        with open('./data/sample.mdx.1', 'wb') as output_header, open('./data/sample.mdx.2', 'wb') as output_2, open('./data/sample.mdx.3', 'wb') as output_key_block_body_body, open('./data/sample.mdx.4', 'wb') as output_4, open('./data/sample.mdx.5', 'wb') as output_record_block_body_body:
            ws = MDictWriterStream(
                title="Example Dictionary",
                description="This is an example dictionary.",
                output_key_block_body_body=output_key_block_body_body,
                output_record_block_body_body=output_record_block_body_body,
                is_mdd=False,
            )
            for k in dictionary:
                ws.add({k: dictionary[k]})

            ws.commit()
            ws.write_1_header(output_header)
            ws.write_2_key_preamble_and_index_and_block_body_header(output_2)
            ws.write_4_record_preamble_and_block_body_header(output_4)

        mergeFiles('./data/sample.mdx', ['./data/sample.mdx.1', './data/sample.mdx.2',
                   './data/sample.mdx.3', './data/sample.mdx.4', './data/sample.mdx.5'])


def mergeFiles(out: str, ins: list):
    BLOCKSIZE = 4096
    BLOCKS = 1024
    chunk = BLOCKS * BLOCKSIZE
    with open(out, "wb") as o:
        for fname in ins:
            with open(fname, "rb") as i:
                o.write(i.read(chunk))
