# -*- coding: utf-8 -*-

import codecs
import re
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

_SECTION = [
    '^[#*=\-^"]{2,}$',     # ===
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

_NOTRANSLATE = _INLINE + _ROLE + _SECTION + _HYPER_LINK + \
               _RUBRIC + _REFFERENCE
_NOTRANSLATE_PTRN = re.compile(r"({0})".format("|".join(_NOTRANSLATE)),
                               re.M | re.U)

_LISTBLOCK = re.compile(r"""(
      ^[*\-\d#]\.*\s+       # * list
    | ^\s+[*\-\d#]\.*\s+    #   * nested list
)(.*?)$""", re.U | re.X)

_LINEBLOCK = re.compile(r"""(
    ^\|\s+  # | line block
)(.*?)$""", re.U | re.X)

_TABLEBLOCK = re.compile(r"""(
      (?P<grid_rule>^\s*\+([\-=]+\+)+\s*)       # grid table rule
    | (?P<grid_rows>^\s*\|(.*?\|)+\s*)          # grid table rows
    | (?P<simple_rule>^\s*=+(\s+=+){2,}\s*)     # simple table rule
    | (?P<simple_rows>^\s*.*?(\s+.*?){2,}\s*)   # simple table rows
)$""", re.U | re.X)

_DIRECTIVE = [
    "^\s*::\s*$",           # source code
    "^\.\..*(?<!::)$",      # comment
    "^\.\.\s+.+::.*$",      # .. xxx:: or .. xxx:: yyy
]

_DIRECTIVE_PTRN = re.compile(r"({0})".format("|".join(_DIRECTIVE)), re.U)

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
_PARAGRAPH_START = re.compile(r"^\S+.*$", re.U)
_END_OF_SENTENCE = {
    "en": re.compile(unicode(r"[\.\?!]", "utf-8"), re.M | re.U),
    "ja": re.compile(unicode(r"[\.\?!。．？！]", "utf-8"), re.M | re.U),
}

class reSTFileHandler(BaseHandler):
    """
    Handler class for translating reST file
    """

    block_type = {
        "directive": "d",
        "lineblock": "ln",
        "listblock": "ls",
        "paragraph": "p",
        "indent_paragraph": "i",
        "tableblock": "t",
    }

    def __init__(self, opts):
        self.lang_to = opts.lang_to
        self.rst_file = opts.rst_file[0]
        self.encoding = opts.encoding
        with codecs.open(self.rst_file, mode="r",
                         encoding=self.encoding[1]) as f:
            lines = f.readlines()  # read out all lines
        self.blocks = self.convert_lines_to_blocks(lines)
        self.out_file = "out.rst"

    def convert_lines_to_blocks(self, lines):
        blocks = []
        skip_num = 0
        for num, line in enumerate(lines):
            if skip_num > 0:
                skip_num -= 1
                continue
            info, skip_num = self.get_directive(num, lines)
            if not info[0]:
                info, skip_num = self.get_lineblock(num, lines)
            if not info[0]:
                info, skip_num = self.get_listblock(num, lines)
            if not info[0]:
                info, skip_num = self.get_tableblock(num, lines)
            if not info[0]:
                info, skip_num = self.get_paragraph(num, lines)
            if not info[0]:
                info, skip_num = self.get_indent_paragraph(num, lines)
            if not info[0]:  # others
                info = (None, [line], None)
            blocks.append(info)
        return blocks

    def get_directive(self, line_num, lines):
        def _get_code_block(_lines):
            num = 0
            for num, line in enumerate(_lines[1:]):
                if line[0:2] == "..":  # directive for single line
                    break
                elif re.search(_PARAGRAPH_START, line):
                    # end of directive block is previous line of current
                    num -= 1
                    break
            if num + 2 == len(_lines):
                # reaching to EOF might not be found _PARAGRAPH_START
                num += 1
            return num, _lines[0:num + 1]

        btype, block, directive, end = None, [], None, 0
        match = re.search(_DIRECTIVE_PTRN, lines[line_num])
        if match:
            btype = self.block_type["directive"]
            directive = match.groups()[0]
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, directive), end

    def get_lineblock(self, line_num, lines):
        btype, block, bnum = None, [], 0
        if re.search(_LINEBLOCK, lines[line_num]):
            btype = self.block_type["lineblock"]
            _cmp = lambda line: not re.search(_LINEBLOCK, line)
            bnum, block = get_sequential_block(lines[line_num:], _cmp)
        return (btype, block, []), bnum

    def get_listblock(self, line_num, lines):
        def _get_code_block(_lines):
            num = 0
            empty = False
            for num, line in enumerate(_lines[1:]):
                if re.search(_EMPTY_LINE, line) and not empty:
                    empty = True
                elif re.search(_LISTBLOCK, line):
                    empty = False
                else:
                    # end of list block is previous line of current
                    num -= 1
                    break
            if num + 2 == len(_lines):
                # reaching to EOF might not be found _PARAGRAPH_START
                num += 1
            return num, _lines[0:num + 1]

        btype, block, listblock, end = None, [], None, 0
        match = re.search(_LISTBLOCK, lines[line_num])
        if match:
            btype = self.block_type["listblock"]
            listblock = match.groups()[0]
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, listblock), end

    def get_tableblock(self, line_num, lines):
        btype, block, bnum = None, [], 0
        match = re.search(_TABLEBLOCK, lines[line_num])
        if match and not match.groupdict().get("simple_rows"):
            btype = self.block_type["tableblock"]
            _cmp = lambda line: not re.search(_TABLEBLOCK, line)
            bnum, block = get_sequential_block(lines[line_num:], _cmp)
        return (btype, block, []), bnum

    def get_paragraph(self, line_num, lines):
        def _get_code_block(_lines):
            num = 0
            for num, line in enumerate(_lines[1:]):
                if line[0:2] == ".." or re.search(_EMPTY_LINE, line):
                    break
            if num + 2 == len(_lines):
                # reaching to EOF might not be found _PARAGRAPH_START
                num += 1
            return num, _lines[0:num + 1]

        btype, block, paragraph, end = None, [], None, 0
        match = re.search(_PARAGRAPH_START, lines[line_num])
        if match:
            btype = self.block_type["paragraph"]
            paragraph = match.group()
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, paragraph), end

    def get_indent_paragraph(self, line_num, lines):
        btype, block, bnum = None, [], 0
        if re.search(_LINE_WITH_INDENT, lines[line_num]):
            btype = self.block_type["indent_paragraph"]
            _cmp = lambda line: re.search(_EMPTY_LINE, line)
            bnum, block = get_sequential_block(lines[line_num:], _cmp)
        return (btype, block, []), bnum

    def get_indent_and_text(self, line):
        indent, text = "", line
        match = re.search(_LINE_WITH_INDENT, line)
        if match:
            indent, text = match.groups()
        return indent, text

    def split_text_into_multiline(self, text):
        def _add_linebreak(lines):
            # FIXME: more simple!
            _section_ptrn = re.compile(r"""
                ([#|*|=|\-|^|"]{2,})?  # section bar or None
                (.*?)                  # section title
                ([#|*|=|\-|^|"]{2,})   # section bar
            """, re.X)
            _lines = []
            indent, lines[0] = self.get_indent_and_text(lines[0])
            for line in lines:
                m = re.findall(_section_ptrn, line)
                if m and isinstance(m[0], tuple):
                    # for section
                    line = "\n".join(m[0]) if m[0][0] else "\n".join(m[0][1:])
                _lines.append(u"{0}{1}\n".format(indent, line))
            return _lines

        lines = [text]
        eos_ptrn = _END_OF_SENTENCE.get(self.lang_to) or _END_OF_SENTENCE["en"]
        sentence_num = len(re.findall(eos_ptrn, text))
        if sentence_num > 0:
            ptrn = u"(.*?{0})".format(eos_ptrn.pattern) * sentence_num
            match = re.findall(ptrn, text)
            if match:
                if isinstance(match[0], tuple):
                    lines = list(match[0])
                else:
                    lines = [match[0]]
        return _add_linebreak(lines)

    def _call_and_split(self, api_method, line):
        _text = self.markup_paragraph_notranslate(line)
        api, result = api_method(_text)
        split_lines = self.split_text_into_multiline(result)
        return api, split_lines

    def _call_keeping_prefix(self, api_method, line, match):
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
        api, lines = None, []
        for line in block_lines:
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
                _items = [i.strip().rstrip() for i in line.split("|")]
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

    def _call_method(self, api_method):
        in_enc, out_enc = self.encoding
        with codecs.open(self.out_file, mode="w", encoding=out_enc) as f:
            for btype, block_lines, first in self.blocks:
                print btype, block_lines
                if btype == self.block_type["directive"]:
                    lines = block_lines
                    if re.search(_DIRECTIVE_WITH_PARAGRAPH, first):
                        ret = self._call_for_directive(
                                api_method, block_lines)
                        lines = ret[1]
                elif btype == self.block_type["lineblock"]:
                    ret = self._call_for_lineblock(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["listblock"]:
                    ret = self._call_for_listblock(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["tableblock"]:
                    ret = self._call_for_tableblock(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["paragraph"]:
                    ret = self._call_for_paragraph(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["indent_paragraph"]:
                    ret = self._call_for_indent_paragraph(
                                    api_method, block_lines)
                    lines = ret[1]
                else:
                    lines = block_lines
                f.writelines(lines)

    @classmethod
    def markup_paragraph_notranslate(self, text):
        text = text.replace(u"&", u"&amp;")
        text = text.replace(u"<", u"&lt;")
        text = text.replace(u">", u"&gt;")
        repl = r"<span class=notranslate>\1</span>"
        return re.sub(_NOTRANSLATE_PTRN, repl, text)
