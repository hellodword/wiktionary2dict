# wiktionary2dict

## TODO

- [x] [sax / pulldom](https://web.archive.org/web/20150108212346/https://www.ibm.com/developerworks/xml/library/x-tipulldom/index.html)
- [x] [bz2 streaming](https://stackoverflow.com/questions/37172679/reading-first-lines-of-bz2-files-in-python)
- [ ] wikitext
- [ ] [mdx/mdd streaming](#mdxmdd-streaming)
- [ ] parallel

## mdx/mdd streaming

- header 固定，单独文件 output_header
- key section 的 `preamble` 和 `preamble_checksum = zlib.adler32(preamble)` 位置和长度固定，可以一直更改（于是可能可以任务暂停/继续？），单独文件 output_key_preamble
- key section 的 block 可以单独一个文件 output_key_block
- record section 的 `preamble` 位置和长度固定，可以一直更改（可以续传），单独文件 output_record_preamble
- record section 的 block 可以单独一个文件 output_record_block
- `zlib.compress` streaming

## About `.vscode`

为了保证我个人的 `devcontainer` 的体验，所以上传了 `.vscode` 文件夹，请勿在意。

## Reference

- https://github.com/tatuylonen/wiktextract/blob/master/wiktwords
- https://github.com/nikita-moor/latin-dictionary/issues/2
- https://github.com/marbu/wiktionary-etymology-dump
- https://github.com/5j9/wikitextparser
- https://bitbucket.org/xwang/mdict-analysis
- https://github.com/liuyug/mdict-utils
- https://github.com/skywind3000/writemdict
- https://github.com/skywind3000/ECDICT/blob/bc6b25957f1dbb745768bb734b20a613edf7fdbe/stardict.py#L1433
- https://github.com/Dictionaryphile/All_Dictionaries
- https://github.com/goldendict/goldendict/wiki/Supported-Dictionary-Formats