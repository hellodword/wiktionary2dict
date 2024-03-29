# wiktionary2dict

## TODO

- [x] [sax / pulldom](https://web.archive.org/web/20150108212346/https://www.ibm.com/developerworks/xml/library/x-tipulldom/index.html)
- [x] [bz2 streaming](https://stackoverflow.com/questions/37172679/reading-first-lines-of-bz2-files-in-python)
- [x] [mdx/mdd streaming](#mdxmdd-streaming)
- [ ] parallel

## mdx/mdd streaming

> 去掉排序后，mdx 无法在 Goldendict Desktop 之外的词典 APP 使用，所以先把解析后的数据放进数据库或者连同偏移存储在文件里，再读取生成

- header 固定，单独文件 output_header
- key section 的 `preamble` 和 `preamble_checksum = zlib.adler32(preamble)` 位置和长度固定，可以一直更改（于是可能可以任务暂停/继续？），单独文件 output_key_preamble
- key section 的 block 可以单独一个文件 output_key_block
- record section 的 `preamble` 位置和长度固定，可以一直更改（可以续传），单独文件 output_record_preamble
- record section 的 block 可以单独一个文件 output_record_block
- `zlib.compress` streaming

## Usage

```sh
pip install -e git+https://github.com/hellodword/wiktionary2dict@master#egg=wiktionary2dict

wget https://dumps.wikimedia.org/simplewiktionary/latest/simplewiktionary-latest-pages-articles.xml.bz2

wiktionary2dict simplewiktionary-latest-pages-articles.xml.bz2 'Wiktionary Simple English 2023' 'simplewiktionary.mdx'
```

## ~~Debug~~

```sh
grep -B 30 -A 6000 '<title>\(free\|idiom\|the\|be\|and\|a\|of\|to\|in\|for\|have\|you\|let\|make\|get\)<' enwiktionary-latest-pages-articles.xml > sample.xml

bzip2 --keep --compress sample.xml

time -p docker exec --user 1000 -it -w /workspaces/wiktionary2dict <devcontainer> python -m wiktionary2dict data/en.sample.xml 'Wiktionary English 2023' 'data/sample.mdx'
# zhwiktionary 18min
# enwiktionary 73min

# match special pages
grep -B 1 '<ns>[1-9\-]' data/enwiktionary-latest-pages-articles.xml | grep -o '<title>[^:]\+:' | sort -n | uniq

# list all wiktionary lang
curl -sSL https://dumps.wikimedia.org/backup-index.html | grep -oP '[a-z]+wiktionary(?=[^a-zA-Z])' | sort -n | uniq

# list all wiktionary lang and size
curl -sSL https://dumps.wikimedia.org/backup-index.html | grep -oP '[a-z]+wiktionary(?=[^a-zA-Z])' | sort -n | uniq \
    | xargs -i sh -c 'echo {} `curl -sSL -f -I https://dumps.wikimedia.org/{}/latest/{}-latest-pages-articles.xml.bz2 | grep -oP "(?<=Content-Length: )\d+"`'
```

### ~~mwlib~~

```sh
# install re2c
wget https://github.com/skvadrik/re2c/releases/download/3.0/re2c-3.0.tar.xz

pip install six py gevent odfpy future reportlab toml

pip install -e git+https://github.com/pediapress/mwlib@python3_upgrade#egg=mwlib
```

## Reference

- https://github.com/tatuylonen/wiktextract/blob/master/wiktwords
- https://github.com/nikita-moor/latin-dictionary/issues/2
- https://github.com/marbu/wiktionary-etymology-dump
- https://github.com/5j9/wikitextparser
- https://bitbucket.org/xwang/mdict-analysis
- https://github.com/liuyug/mdict-utils
- https://github.com/skywind3000/writemdict
- https://github.com/liuyug/mdict-utils
- https://github.com/skywind3000/ECDICT/blob/bc6b25957f1dbb745768bb734b20a613edf7fdbe/stardict.py#L1433
- https://github.com/Dictionaryphile/All_Dictionaries
- https://github.com/goldendict/goldendict/wiki/Supported-Dictionary-Formats
- https://github.com/TrueBrain/wikitexthtml
- https://github.com/lunaroyster/vue-wikitext
- https://pypi.org/project/mwlib/
- https://stackoverflow.com/a/28783167
- https://github.com/wikimedia/pywikibot
- https://github.com/earwig/mwparserfromhell
- https://mwlib.readthedocs.io/en/latest/commands.html#the-mw-render-command
- https://github.com/derhuerst/render-wikipedia-article
- https://github.com/dustin/go-wikiparse
- https://github.com/wikimedia/mediawiki/blob/a4da635e8a2f00fd317cc458b6787cba17efc452/maintenance/parse.php#L83-L89
- https://github.com/wikimedia/mediawiki-services-parsoid/tree/master/src/Wt2Html
- https://github.com/wincent/wikitext