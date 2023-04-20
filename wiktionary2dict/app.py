from .writemdict.writemdict import MDictWriter as MDictWriterStream

from html import escape
from collections import defaultdict
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
    wikitext_cb: Callable[[str, WikiText, str], any] = None,
):

    def redirect_handle(title: str, redirect: str):
        if redirect_cb is not None:
            redirect_cb(title, redirect)
        return None

    def template_handle(title: str, text: str):
        # TODO
        return None

    def wikitext_handle(title: str, text: str):
        if title is None or title == '':
            return None

        if text is None:
            return None

        w = WikiText(text)
        if w is None:
            return None

        if wikitext_cb is not None:
            wikitext_cb(title, w, text)

    def page_handle(node: Element) -> Tuple[str | None, str | None, str | WikiText | None]:
        ns = getElementTextByTagName(node, 'ns')
        if ns is None:
            return

        title = getElementTextByTagName(node, 'title')
        if title is None or title == '':
            return

        if ns == '0':
            redirects = node.getElementsByTagName('redirect')
            if redirects.length > 0:
                return redirect_handle(
                    title,
                    redirects[0].getAttribute('title'),
                )

            model = getElementTextByTagName(node, 'model')
            if model == 'wikitext':
                return wikitext_handle(
                    title,
                    getElementTextByTagName(node, 'text'),
                )
        elif ns == '10':
            return template_handle(
                title,
                getElementTextByTagName(node, 'text'),
            )
        elif ns == '8':
            # TODO MediaWiki
            return
        elif ns == '14':
            # TODO Category
            return
        elif ns == '100':
            # TODO Appendix
            return
        else:
            # TODO
            return

        return

    with BZ2OrXml(path) as f:
        events = pulldom.parse(f)

        for (event, node) in events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'page':
                    events.expandNode(node)
                    page_handle(node)


def mergeFiles(out: str, ins: list):
    BLOCKSIZE = 4096
    BLOCKS = 1024
    chunk = BLOCKS * BLOCKSIZE
    with open(out, "wb") as o:
        for fname in ins:
            with open(fname, "rb") as i:
                b = i.read(chunk)
                while len(b) > 0:
                    o.write(b)
                    b = i.read(chunk)


class Wiktionary2Dict:

    @staticmethod
    def run():

        with open('./data/sample.mdx.1', 'wb') as output_header, open('./data/sample.mdx.2', 'wb') as output_2, open('./data/sample.mdx.3', 'wb') as output_key_block_body_body, open('./data/sample.mdx.4', 'wb') as output_4, open('./data/sample.mdx.5', 'wb') as output_record_block_body_body:
            ws = MDictWriterStream(
                title="Wiktionary English",
                description="This is an example dictionary.",
                output_key_block_body_body=output_key_block_body_body,
                output_record_block_body_body=output_record_block_body_body,
                is_mdd=False,
            )

            # for example
            def gen_html(w: WikiText) -> str:
                h = ''
                sections2 = w.get_sections(include_subsections=True, level=2)
                for s2 in sections2:
                    h += f'<h2>{escape(s2.title)}</h2>'
                    sections3 = s2.get_sections(include_subsections=False, level=3)
                    for s3 in sections3:
                        h += f'<h3>{escape(s3.title)}</h3>'
                return h

            def wikitext_cb(title: str, w: WikiText, text: str):
                ws.add({title: gen_html(w)})
                return

            parse_wiktionary('./data/en.sample.xml.bz2', wikitext_cb=wikitext_cb)

            ws.commit()
            ws.write_1_header(output_header)
            ws.write_2_key_preamble_and_index_and_block_body_header(output_2)
            ws.write_4_record_preamble_and_block_body_header(output_4)

        mergeFiles('./data/sample.mdx',
                   [
                       './data/sample.mdx.1',
                       './data/sample.mdx.2',
                       './data/sample.mdx.3',
                       './data/sample.mdx.4',
                       './data/sample.mdx.5',
                   ])
