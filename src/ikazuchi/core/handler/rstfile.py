# -*- coding: utf-8 -*-

import codecs
import re
import textwrap
from base import BaseHandler
from ikazuchi.core.translator.utils import call_api_with_multithread
from utils import *

try:
    from ikazuchi.locale import _
except ImportError:
    def _(s): return s

_INLINE = [
    "\*+.*?\*+",    # italic or bold
    "``.*?``",      # literal
]

_ROLE = [
    ":.*?:`.*?`",   # :role:`xxx`
]

_HYPER_LINK = [
    "`.*?\s*`_",    # `link <http://xxx>`_ or `link`_
    "^\.\.\s*_.*?:\s*http.*$",  # .. _link: http://xxx
]

_RUBRIC = [
    "\[#.*\]_",                 # [#f1]_
    "^\.\.\s*\[#.*\].*$",       # .. [#f1] description
]

_REFFERENCE = [
    "\[(?!#).*?\]_",            # [ref]_
    "^\.\.\s*\[(?!#).*?\].*$",  # .. [ref] description
]

_SOURCE = [
    ":\s+",     # collon:
    "::\s*",    # source::
]

_NOTRANSLATE = _INLINE + _ROLE + _HYPER_LINK + _RUBRIC + _REFFERENCE + _SOURCE
_NOTRANSLATE_PTRN = re.compile(r"({0})".format("|".join(_NOTRANSLATE)),
                               re.M | re.U)

_SECTION = re.compile(r"""
    (?P<over_line>[#*=\-^"]{2,}\s+)?    # =======
    (?P<section>.*?\s+)                 # section
    (?P<under_line>[#*=\-^"]{2,}\s+)$   # =======
""", re.U | re.X)

_SECTION_LINE = re.compile(r'^[#*=\-^"]{2,}\s+', re.U)

_LISTBLOCK = re.compile(r"""(
      ^[*\-\d#]\.*\s+       # * list
    | ^\s+[*\-\d#]\.*\s+    #   * nested list
)(.*?)$""", re.U | re.X)

_LINEBLOCK = re.compile(r"""
      (^\|\s+)(.+?)$    # | line block
    | (^\|\s*)$         # |
""", re.U | re.X)

_TABLEBLOCK = re.compile(r"""(
      (?P<grid_rule>^\s*\+([\-=]+\+)+\s*)       # grid table rule
    | (?P<grid_rows>^\s*\|(.*?\|)+\s*)          # grid table rows
    | (?P<simple_rule>^\s*=+(\s+=+){2,}\s*)     # simple table rule
    | (?P<simple_rows>^\s*.*?(\s+.*?){2,}\s*)   # simple table rows
)$""", re.U | re.X)

_SOURCE_CODE = re.compile(r"^.*?::\s*$", re.U)

_DIRECTIVE = re.compile(r"""(
      {0}               # source code
    | ^\.\..*(?<!::)    # comment
    | ^\.\.\s+.+::.*    # .. xxx:: or .. xxx:: yyy
)$""".format(_SOURCE_CODE), re.U | re.X)

_DIRECTIVE_WITH_PARAGRAPH = re.compile(r"""(
      ^\.\.\s+note::        # .. note::
    | ^\.\.\s+warning::     # .. warning::
    | ^\.\.\s+seealso::     # .. seealso::
    | ^\.\.\s+rubric::      # .. rubric::
    | ^\.\.\s+tip::         # .. tip::
    | ^\.\.\s+error::       # .. error::
    | ^\.\.\s+hint::        # .. hint::
    | ^\.\.\s+important::   # .. important::
    | ^\.\.\s+attention::   # .. attention::
    | ^\.\.\s+caution::     # .. caution::
    | ^\.\.\s+danger::      # .. danger::
).*$""", re.U | re.X)

_EMPTY_LINE = re.compile(r"^\s*$", re.U)
_LINE_WITH_INDENT = re.compile(r"(^\s+)(.+?)$", re.U)
_PARAGRAPH_START = re.compile(r"^([\S\.]+)(.*?)$", re.U)
_END_OF_SENTENCE = {
    "en": re.compile(unicode(r".*?[\.\?!]", "utf-8"), re.M | re.U),
    "ja": re.compile(unicode(r".*?[。．？！]", "utf-8"), re.M | re.U),
}

REST_BLOCK_TYPE = {
    "directive": "d",
    "lineblock": "ln",
    "listblock": "ls",
    "paragraph": "p",
    "indent_paragraph": "i",
    "tableblock": "t",
    "section": "se",
    "source": "so",
}


class reSTFileHandler(BaseHandler):
    """
    Handler class for translating reST file
    """
    def __init__(self, opts):
        self.rst_file = opts.rst_file[0]
        self.encoding = opts.encoding
        with codecs.open(self.rst_file, mode="r",
                         encoding=self.encoding[1]) as f:
            lines = f.readlines()  # read out all lines
        blocks = reSTParser(lines).parse()
        self.caller = reSTApiCaller(blocks, opts.lang_to)
        self.output = "output.rst"

    def _call_method(self, api_method):
        in_enc, out_enc = self.encoding
        with codecs.open(self.output, mode="w", encoding=out_enc) as f:
            for lines in self.caller.call(api_method):
                f.writelines(lines)


class reSTParser(object):
    """
    Parser class for reading/parsing lines with reST format
    """
    def __init__(self, lines):
        self.lines = lines

    def _convert_lines_to_blocks(self, lines):
        blocks = []
        skip_num = 0
        for num, line in enumerate(lines):
            if skip_num > 0:
                skip_num -= 1
                continue
            _lines = lines[num:]
            info, skip_num = self.get_directive(_lines)
            if not info[0]:
                info, skip_num = self.get_sourceblock(_lines)
            if not info[0]:
                info, skip_num = self.get_lineblock(_lines)
            if not info[0]:
                info, skip_num = self.get_listblock(_lines)
            if not info[0]:
                info, skip_num = self.get_tableblock(_lines)
            if not info[0]:
                info, skip_num = self.get_section(_lines)
            if not info[0]:
                info, skip_num = self.get_paragraph(_lines)
            if not info[0]:
                info, skip_num = self.get_indent_paragraph(_lines)
            if not info[0]:  # others
                info = (None, [line], None)
            blocks.append(info)
        return blocks

    def parse(self):
        return self._convert_lines_to_blocks(self.lines)

    @classmethod
    def get_directive(self, lines):
        btype, block, directive, bnum = None, [], u"", 0
        match = re.search(_DIRECTIVE, lines[0])
        if match:
            btype = REST_BLOCK_TYPE["directive"]
            directive = match.groups()[0]
            bnum, block = 0, lines[0:1]
            if not lines[1][0:2] == "..":
                _cmp = lambda line: re.search(_PARAGRAPH_START, line)
                bnum, block = get_sequential_block(lines, _cmp)
        return (btype, block, directive), bnum

    @classmethod
    def get_sourceblock(self, lines):
        def _get_code_block(_lines):
            btype, first, num = None, u"", 0
            for num, mline in enumerate(get_multiline(_lines, 2)):
                if not btype and re.search(_SOURCE_CODE, mline[0]) and \
                   (re.search(_EMPTY_LINE, mline[1]) or \
                    re.search(_LINE_WITH_INDENT, mline[1])):
                    btype = REST_BLOCK_TYPE["source"]
                    first = u"".join(_lines[0:num + 1])
                elif re.search(_EMPTY_LINE, mline[0]) and \
                     not re.search(_LINE_WITH_INDENT, mline[1]):
                    break
            else:
                # maybe read out to EOF
                num += 1
            return (btype, _lines[0:num + 1], first), num

        return _get_code_block(lines)

    @classmethod
    def get_lineblock(self, lines):
        btype, block, bnum = None, [], 0
        if re.search(_LINEBLOCK, lines[0]):
            btype = REST_BLOCK_TYPE["lineblock"]
            _cmp = lambda line: not re.search(_LINEBLOCK, line)
            bnum, block = get_sequential_block(lines, _cmp)
        return (btype, block, u""), bnum

    @classmethod
    def get_listblock(self, lines):
        def _get_code_block(_lines):
            num = 0
            for num, mline in enumerate(get_multiline(_lines, 2)):
                if re.search(_LISTBLOCK, mline[0]) or \
                   re.search(_LINE_WITH_INDENT, mline[0]) or \
                   (re.search(_EMPTY_LINE, mline[0]) and \
                    re.search(_LISTBLOCK, mline[1])):
                    pass
                else:
                    break
            else:
                # maybe read out to EOF
                num += 1
            return num, _lines[0:num + 1]

        btype, block, bnum = None, [], 0
        match = re.search(_LISTBLOCK, lines[0])
        if match:
            btype = REST_BLOCK_TYPE["listblock"]
            bnum, block = _get_code_block(lines)
        return (btype, block, u""), bnum

    @classmethod
    def get_tableblock(self, lines):
        btype, block, bnum = None, [], 0
        match = re.search(_TABLEBLOCK, lines[0])
        if match and not match.groupdict().get("simple_rows"):
            btype = REST_BLOCK_TYPE["tableblock"]
            _cmp = lambda line: not re.search(_TABLEBLOCK, line)
            bnum, block = get_sequential_block(lines, _cmp)
        return (btype, block, u""), bnum

    @classmethod
    def get_section(self, lines):
        def _get_code_block(_lines):
            num, section = 0, []
            for mline in get_multiline(_lines, 3):
                match = re.search(_SECTION, "".join(mline))
                if re.search(_EMPTY_LINE, mline[0]) or \
                   re.search(_EMPTY_LINE, mline[1]):
                    break
                elif match:
                    d = match.groupdict()
                    if d.get("section"):
                        if d.get("over_line") or d.get("under_line"):
                            num, section = 2, mline
                            break
            return num, section

        btype = None
        bnum, block = _get_code_block(lines)
        if bnum > 0:
            btype = REST_BLOCK_TYPE["section"]
        return (btype, block, u""), bnum

    @classmethod
    def get_paragraph(self, lines):
        btype, block, bnum = None, [], 0
        match = re.search(_PARAGRAPH_START, lines[0])
        if match:
            btype = REST_BLOCK_TYPE["paragraph"]
            _cmp = lambda line: re.search(_EMPTY_LINE, line)
            bnum, block = get_sequential_block(lines, _cmp)
        return (btype, block, u""), bnum

    @classmethod
    def get_indent_paragraph(self, lines):
        btype, block, bnum = None, [], 0
        if re.search(_LINE_WITH_INDENT, lines[0]):
            btype = REST_BLOCK_TYPE["indent_paragraph"]
            _cmp = lambda line: re.search(_EMPTY_LINE, line)
            bnum, block = get_sequential_block(lines, _cmp)
        return (btype, block, u""), bnum


class reSTApiCaller(object):
    """
    Caller class for converting reST block calling api method
    """
    def __init__(self, blocks, lang_to):
        self.blocks = blocks
        self.lang_to = lang_to

    def get_indent_and_text(self, line):
        indent, text = "", line
        match = re.search(_LINE_WITH_INDENT, line)
        if match:
            indent, text = match.groups()
        return indent, text

    def split_text_into_multiline(self, text):
        if self.lang_to in ("ja"):
            eos_ptrn = _END_OF_SENTENCE.get(self.lang_to)
            _lines = re.findall(eos_ptrn, text)
            if not _lines:
                _lines = [text]
            else:
                extra_text = text[len(u"".join(_lines)):]
                if extra_text:
                    _lines.append(extra_text)
            indent, _ = self.get_indent_and_text(_lines[0])
            return [u"{0}{1}\n".format(indent, line) for line in _lines]
        else:
            indent, _ = self.get_indent_and_text(text)
            dedented_text = textwrap.dedent(text).strip()
            indented = textwrap.fill(dedented_text, initial_indent=indent,
                                        subsequent_indent=indent)
            return [indented]

    def _call_and_split(self, api_method, line):
        _text = self.markup_paragraph_notranslate(line)
        api, result = api_method(_text)
        split_lines = self.split_text_into_multiline(result)
        return api, split_lines

    def _call_keeping_prefix(self, api_method, line, match):
        prefix, text = "", line
        if match:
            prefix, text = match.groups()
        _text = self.markup_paragraph_notranslate(text)
        api, result = api_method(_text)
        return api, u"{0}{1}\n".format(prefix, result)

    def _call_for_directive(self, api_method, block_lines):
        def _concatenate_lines(lines):
            _lines, prev_indent = [], None
            for line in lines:
                match = re.search(_LINE_WITH_INDENT, line)
                if re.search(_EMPTY_LINE, line) or not match:
                    _lines.append(line)
                    prev_indent = None
                else:
                    indent, text = match.groups()
                    if prev_indent == indent:
                        _prev = _lines[-1].rstrip()
                        _lines[-1] = u"{0} {1}".format(_prev, text)
                    else:
                        _lines.append(line)
                    prev_indent = indent
            return _lines

        api, lines = None, block_lines[:1]
        for line in _concatenate_lines(block_lines[1:]):
            match = re.search(_LINE_WITH_INDENT, line)
            if match and not re.search(_EMPTY_LINE, line):
                api, line = self._call_keeping_prefix(api_method, line, match)
            lines.append(line)
        return api, lines

    def _call_for_lineblock(self, api_method, block_lines):
        api, lines = None, []
        for line in block_lines:
            match = re.match(_LINEBLOCK, line)
            if match:
                api, line = self._call_keeping_prefix(api_method, line, match)
            lines.append(line)
        return api, lines

    def _call_for_listblock(self, api_method, block_lines):
        def _concatenate_lines(lines):
            # FIXME: need more simple!
            _lines, _text = [], u""
            for mline in get_multiline(lines, 2):
                if re.search(_LISTBLOCK, mline[0]):
                    if re.search(_LINE_WITH_INDENT, mline[1]):
                        _text = mline[0]
                    else:
                        _lines.append(mline[0])
                elif re.search(_EMPTY_LINE, mline[0]):
                    _lines.append(u"{0}".format(_text))
                    _lines.append(mline[0])
                    _text = u""
                else:
                    _text = u"{0} {1}".format(_text.rstrip(),
                                              mline[0].lstrip())
            else:
                if _text:
                    _lines.append(u"{0}".format(_text))
                if re.search(_LISTBLOCK, mline[1]) or \
                   re.search(_EMPTY_LINE, mline[1]):
                    _lines.append(mline[1])
            return _lines

        api, lines = None, []
        for line in _concatenate_lines(block_lines):
            match = re.match(_LISTBLOCK, line)
            if match and not re.search(_EMPTY_LINE, line):
                api, line = self._call_keeping_prefix(api_method, line, match)
            lines.append(line)
        return api, lines

    def _get_table_column_width(self, max_width, east_asian_width, items):
        _columns = []
        for num, text in enumerate(items):
            text_width = get_east_asian_width(text)
            if max_width[num] < text_width:
                max_width[num] = text_width
            _columns.append(text_width)
        east_asian_width.append(_columns)

    def _call_for_gridtable(self, api_method, block_lines, column_length):
        api, results = None, []
        # remove first/last column since it is empty column
        max_width = [0] * (column_length - 2)
        east_asian_width = []
        for line in block_lines:
            indent, line = self.get_indent_and_text(line)
            d = re.search(_TABLEBLOCK, line).groupdict()
            if d.get("grid_rule"):
                items = line.split("+")[1:-1]
            elif d.get("grid_rows"):
                _items = [i.strip() for i in line.split("|")]
                _items = map(self.markup_paragraph_notranslate, _items[1:-1])
                items = call_api_with_multithread(api_method, _items)
                api = items[0][0]
                items = [text for _, text in items]
            else:
                items = [line]
            self._get_table_column_width(max_width, east_asian_width, items)
            results.append(items)

        # format table block considering its width
        lines = []
        rule_fmt = u"#+#".join(u"{%s:{%s}}" % (num, num + 1)
                            for num in range(0, len(max_width) * 2, 2))
        rule_fmt = u"+#{0}{1}#+\n".format(indent, rule_fmt)
        row_fmt = u" | ".join(u"{%s:{%s}}" % (num, num + 1)
                            for num in range(0, len(max_width) * 2, 2))
        row_fmt = u"| {0}{1} |\n".format(indent, row_fmt)
        for rnum, row in enumerate(results):
            _width = list(max_width)  # copy
            len_width = map(len, row)
            rule_flag = False
            if re.search(r"[\-=]+\s*", row[0], re.U):
                rule_flag = True
            for cnum, col in enumerate(row):
                if rule_flag:
                    row[cnum] = col[0] * max_width[cnum]
                else:
                    _width[cnum] = max_width[cnum] - (
                        east_asian_width[rnum][cnum] - len_width[cnum])
            if rule_flag:
                _line = rule_fmt.format(*zip_with_flatlist(row, _width))
                _line = _line.replace("#", row[0][0])
            else:
                _line = row_fmt.format(*zip_with_flatlist(row, _width))
            lines.append(_line)
        return api, lines

    def _call_for_simpletable(self, api_method, block_lines, column_length):
        api, results = None, []
        max_width = [0] * column_length
        east_asian_width = []
        for line in block_lines:
            indent, line = self.get_indent_and_text(line)
            d = re.search(_TABLEBLOCK, line).groupdict()
            if d.get("simple_rule"):
                items = line.split()
                simple_rule_width = map(len, items)
            elif d.get("simple_rows"):
                _items = []
                for column_width in simple_rule_width:
                    _text = line[0:column_width].strip()
                    _items.append(self.markup_paragraph_notranslate(_text))
                    line = line[column_width:].strip()  # overwrite line
                items = call_api_with_multithread(api_method, _items)
                api = items[0][0]
                items = [text for _, text in items]
            else:
                items = [line]
            self._get_table_column_width(max_width, east_asian_width, items)
            results.append(items)

        # format table block considering its width
        lines = []
        fmt = u"  ".join(u"{%s:{%s}}" % (num, num + 1)
                         for num in range(0, len(max_width) * 2, 2))
        fmt = u"{0}{1}\n".format(indent, fmt)
        for rnum, row in enumerate(results):
            _width = list(max_width)  # copy
            len_width = map(len, row)
            for cnum, col in enumerate(row):
                if re.search(r"=+", col, re.U):
                    row[cnum] = col[0] * max_width[cnum]
                else:
                    _width[cnum] = max_width[cnum] - (
                        east_asian_width[rnum][cnum] - len_width[cnum])
            lines.append(fmt.format(*zip_with_flatlist(row, _width)))
        return api, lines

    def _call_for_tableblock(self, api_method, block_lines):
        def _get_column_length(line):
            table_type, length = None, 0
            match = re.search(_TABLEBLOCK, line)
            if match:
                d = match.groupdict()
                if d.get("grid_rule"):
                    table_type = "grid"
                    length = len(line.split("+"))
                elif d.get("simple_rule"):
                    table_type = "simple"
                    length = len(line.split())
            return table_type, length

        table_type, col_len = _get_column_length(block_lines[0])
        max_width = [0] * col_len
        if table_type == "grid":
            ret = self._call_for_gridtable(api_method, block_lines, col_len)
        elif table_type == "simple":
            ret = self._call_for_simpletable(api_method, block_lines, col_len)
        return ret

    def _call_for_section(self, api_method, block_lines):
        api, results, width = None, [], 0
        for line in block_lines:
            if not re.search(_EMPTY_LINE, line) and \
               not re.search(_SECTION_LINE, line):
                match = re.search(_LINE_WITH_INDENT, line)
                api, line = self._call_keeping_prefix(api_method, line, match)
                width = get_east_asian_width(line) - 1  # -1 is linebreak
            results.append(line)

        lines = []
        for num, line in enumerate(results):
            if re.search(r'[#*=\-^"]{2,}\s+', line):
                line = u"{0}\n".format(line[0] * width)
            lines.append(line)
        return api, lines

    def _concatenate_paragraph_line(self, lines):
        _lines, prev_indent = [], None
        for line in lines:
            match = re.search(_LINE_WITH_INDENT, line)
            if re.search(_EMPTY_LINE, line):
                _lines.append(line)
                prev_indent = None
            elif match:
                indent, text = match.groups()
                if prev_indent == indent:
                    _prev = _lines[-1].rstrip()
                    _lines[-1] = u"{0} {1}".format(_prev, text)
                else:
                    _lines.append(line)
                prev_indent = indent
            elif _lines[-1:]:
                _lines[-1] = u"{0} {1}".format(_lines[-1].rstrip(), line)
                prev_indent = None
            else:
                _lines.append(line)
        return _lines

    def _call_for_paragraph(self, api_method, block_lines):
        api, lines = None, []
        for line in self._concatenate_paragraph_line(block_lines):
            match = re.search(_LINE_WITH_INDENT, line)
            if re.search(_EMPTY_LINE, line):
                lines.append(line)
            else:
                if match:
                    api, line = self._call_keeping_prefix(
                                    api_method, line, match)
                    split_lines = self.split_text_into_multiline(line)
                else:
                    api, split_lines = self._call_and_split(api_method, line)
                lines.extend(split_lines)
        return api, lines

    def _call_for_indent_paragraph(self, api_method, block_lines):
        api, lines = None, []
        for line in self._concatenate_paragraph_line(block_lines):
            match = re.search(_LINE_WITH_INDENT, line)
            if match:
                api, line = self._call_keeping_prefix(api_method, line, match)
                lines.extend(self.split_text_into_multiline(line))
            else:
                lines.append(line)
        return api, lines

    def call(self, api_method):
        for btype, block_lines, first in self.blocks:
            print btype, block_lines
            if btype == REST_BLOCK_TYPE["directive"]:
                lines = block_lines
                if re.search(_DIRECTIVE_WITH_PARAGRAPH, first):
                    ret = self._call_for_directive(
                            api_method, block_lines)
                    lines = ret[1]
            elif btype == REST_BLOCK_TYPE["source"]:
                _src = first.split("\n")
                ret = self._call_for_paragraph(api_method, _src)
                ret[1].append("\n")
                lines = ret[1] + block_lines[len(_src):]
            elif btype == REST_BLOCK_TYPE["lineblock"]:
                ret = self._call_for_lineblock(api_method, block_lines)
                lines = ret[1]
            elif btype == REST_BLOCK_TYPE["listblock"]:
                ret = self._call_for_listblock(api_method, block_lines)
                lines = ret[1]
            elif btype == REST_BLOCK_TYPE["tableblock"]:
                ret = self._call_for_tableblock(api_method, block_lines)
                lines = ret[1]
            elif btype == REST_BLOCK_TYPE["section"]:
                ret = self._call_for_section(api_method, block_lines)
                lines = ret[1]
            elif btype == REST_BLOCK_TYPE["paragraph"]:
                ret = self._call_for_paragraph(api_method, block_lines)
                lines = ret[1]
            elif btype == REST_BLOCK_TYPE["indent_paragraph"]:
                ret = self._call_for_indent_paragraph(
                                api_method, block_lines)
                lines = ret[1]
            else:
                lines = block_lines
            yield lines

    @classmethod
    def markup_paragraph_notranslate(self, text):
        text = text.replace(u"&", u"&amp;")
        text = text.replace(u"<", u"&lt;")
        text = text.replace(u">", u"&gt;")
        repl = r"<span class=notranslate>\1</span>"
        return re.sub(_NOTRANSLATE_PTRN, repl, text)
