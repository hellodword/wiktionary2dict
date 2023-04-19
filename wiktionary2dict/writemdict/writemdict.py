from __future__ import unicode_literals
import datetime
from io import BufferedWriter

import struct
import zlib
from html import escape


class ParameterError(Exception):
    # Raised when some parameter to MdxWriter is invalid or uninterpretable.
    pass


class ZlibWriter(object):

    def __init__(self, output):
        self._output = output
        self._size = 0
        self._size_compressed = 0
        self._compressor = zlib.compressobj()

    def write(self, data):
        self._size += len(data)
        compressed = self._compressor.compress(data)
        self._output.write(compressed)
        self._size_compressed += len(compressed)

    def finish(self):
        compressed = self._compressor.flush()
        self._output.write(compressed)
        self._size_compressed += len(compressed)


def _mdx_compress(data, compression_type=2):
    header = (struct.pack(b"<L", compression_type) +
              struct.pack(b">L", zlib.adler32(data) & 0xffffffff))  # depending on python version, zlib.adler32 may return a signed number.
    if compression_type == 0:  # no compression
        return header + data
    elif compression_type == 2:
        return header + zlib.compress(data)
    else:
        raise ParameterError("Unknown compression type")


class MDictWriter(object):

    def __init__(self, title, description,
                 output_key_block_body_body,
                 output_record_block_body_body,
                 day=datetime.date.today(),
                 is_mdd=False,
                 ):
        """
        Prepares the records. A subsequent call to write() writes 
        the mdx or mdd file.

        d is a dictionary. The keys should be (unicode) strings. If used for an mdx
          file (the parameter is_mdd is False), then the values should also be 
          (unicode) strings, containing HTML snippets. If used to write an mdd
          file (the parameter is_mdd is True), then the values should be binary 
          strings (bytes objects), containing the raw data for the corresponding 
          file object.

        title is a (unicode) string, with the title of the dictionary
          description is a (unicode) string, with a short description of the
          dictionary.

        is_mdd is a boolean specifying whether the file written will be an mdx file
          or an mdd file. By default this is False, meaning that an mdd file will
          be written.
        """

        self._title = title
        self._description = description
        self._day = day
        self._is_mdd = is_mdd
        self._compression_type = 2

        self._key_block_body_body_output = ZlibWriter(output_key_block_body_body)
        self._key_block_body_body_checksum = 1
        self._record_block_body_body_output = ZlibWriter(output_record_block_body_body)
        self._record_block_body_body_checksum = 1

        self._num_entries = 0
        self._total_record_len = 0

        self._first_key = None

        # encoding is set to the string used in the mdx header.
        # python_encoding is passed on to the python .encode()
        # function to encode the data.
        # encoding_length is the size of one unit of the encoding,
        # used to calculate the length for keys in the key index.
        if not is_mdd:
            self._python_encoding = "utf_8"
            self._encoding = "UTF-8"
            self._encoding_length = 1
        else:
            self._python_encoding = "utf_16_le"
            self._encoding_length = 2

    def commit(self):
        self._key_block_body_body_output.finish()
        self._record_block_body_body_output.finish()

    def add(self, d):
        self._num_entries += len(d)
        items = list(d.items())
        for key, record in items:
            key_enc = key.encode(self._python_encoding)
            key_null = (key+"\0").encode(self._python_encoding)
            key_len = len(key_enc) // self._encoding_length

            if self._first_key is None:
                self._first_key = key_null
                self._first_key_len = key_len

            self._last_key = key_null
            self._last_key_len = key_len

            # set record_null to a the the value of the record. If it's
            # an MDX file, append an extra null character.
            if self._is_mdd:
                record_null = record
            else:
                record_null = (record+"\0").encode(self._python_encoding)

            key_block_body_body = struct.pack(b">Q", self._total_record_len)+key_null
            self._key_block_body_body_checksum = zlib.adler32(key_block_body_body, self._key_block_body_body_checksum)
            self._key_block_body_body_output.write(key_block_body_body)

            record_block_body_body = record_null
            self._record_block_body_body_checksum = zlib.adler32(
                record_block_body_body, self._record_block_body_body_checksum)
            self._record_block_body_body_output.write(record_block_body_body)

            self._total_record_len += len(record_null)

    def write_1_header(self, f):
        encrypted = 0
        register_by_str = ""
        regcode = ""

        if not self._is_mdd:
            header_string = (
                """<Dictionary """
                """GeneratedByEngineVersion="{version}" """
                """RequiredEngineVersion="{version}" """
                """Encrypted="{encrypted}" """
                """Encoding="{encoding}" """
                """Format="Html" """
                """CreationDate="{date.year}-{date.month}-{date.day}" """
                """Compact="No" """
                """Compat="No" """
                """KeyCaseSensitive="No" """
                """Description="{description}" """
                """Title="{title}" """
                """DataSourceFormat="106" """
                """StyleSheet="" """
                """RegisterBy="{register_by_str}" """
                """RegCode="{regcode}"/>\r\n\x00""").format(
                version='2.0',
                encrypted=encrypted,
                encoding=self._encoding,
                date=self._day,
                description=escape(self._description, quote=True),
                title=escape(self._title, quote=True),
                register_by_str=register_by_str,
                regcode=regcode
            ).encode("utf_16_le")
        else:
            header_string = (
                """<Library_Data """
                """GeneratedByEngineVersion="{version}" """
                """RequiredEngineVersion="{version}" """
                """Encrypted="{encrypted}" """
                """Format="" """
                """CreationDate="{date.year}-{date.month}-{date.day}" """
                """Compact="No" """
                """Compat="No" """
                """KeyCaseSensitive="No" """
                """Description="{description}" """
                """Title="{title}" """
                """DataSourceFormat="106" """
                """StyleSheet="" """
                """RegisterBy="{register_by_str}" """
                """RegCode="{regcode}"/>\r\n\x00""").format(
                version='2.0',
                encrypted=encrypted,
                date=self._day,
                description=escape(self._description, quote=True),
                title=escape(self._title, quote=True),
                register_by_str=register_by_str,
                regcode=regcode
            ).encode("utf_16_le")
        f.write(struct.pack(b">L", len(header_string)))
        f.write(header_string)
        f.write(struct.pack(b"<L", zlib.adler32(header_string) & 0xffffffff))

    def write_2_key_preamble_and_index_and_block_body_header(self, f: BufferedWriter):

        key_block_body_header = (struct.pack(b"<L", self._compression_type) +
                                 struct.pack(b">L", self._key_block_body_body_checksum & 0xffffffff))

        long_format = b">Q"
        short_format = b">H"
        key_index_decomp = (
            struct.pack(long_format, self._num_entries)
            + struct.pack(short_format, self._first_key_len)
            + self._first_key
            + struct.pack(short_format, self._last_key_len)
            + self._last_key
            + struct.pack(long_format, len(key_block_body_header)+self._key_block_body_body_output._size_compressed)
            + struct.pack(long_format, self._key_block_body_body_output._size)
        )

        key_index_comp = _mdx_compress(key_index_decomp)

        preamble = struct.pack(b">QQQQQ",
                               1,  # len(self._key_blocks),
                               self._num_entries,
                               len(key_index_decomp),
                               len(key_index_comp),
                               len(key_block_body_header)+self._key_block_body_body_output._size_compressed)
        preamble_checksum = struct.pack(b">L", zlib.adler32(preamble))

        f.write(preamble)
        f.write(preamble_checksum)

        f.write(key_index_comp)

        f.write(key_block_body_header)

    def write_3_key_block_body_body(self):
        raise Exception("error")

    def write_4_record_preamble_and_block_body_header(self, f: BufferedWriter):
        record_block_body_header = (struct.pack(b"<L", self._compression_type) +
                                    struct.pack(b">L", self._record_block_body_body_checksum & 0xffffffff))

        record_index_decomp = struct.pack(b">QQ",
                                          len(record_block_body_header) +
                                          self._record_block_body_body_output._size_compressed,
                                          self._record_block_body_body_output._size)

        preamble = struct.pack(b">QQQQ",
                               1,  # len(self._record_blocks),
                               self._num_entries,
                               len(record_index_decomp),
                               len(record_block_body_header) +
                               self._record_block_body_body_output._size_compressed)

        f.write(preamble)
        f.write(record_index_decomp)
        f.write(record_block_body_header)

    def write_5_record_block_body_body(self):
        raise Exception("error")
