# -*- coding: utf-8 -*-

import codecs
import re
from base import BaseHandler
from ikazuchi.core.translator.utils import call_api_with_multithread

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
    '^[#|*|=|\-|^|"]{2,}$',     # ===
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
        def _get_code_block(_lines):
            num = 0
            for num, line in enumerate(_lines):
                if not re.search(_LINEBLOCK, line):
                    # end of line block is previous line of current
                    num -= 1
                    break
            return num, _lines[0:num + 1]

        btype, block, lineblock, end = None, [], None, 0
        match = re.search(_LINEBLOCK, lines[line_num])
        if match:
            btype = self.block_type["lineblock"]
            lineblock = match.groups()[0]
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, lineblock), end

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

    def get_paragraph(self, line_num, lines):
        def _get_code_block(_lines):
            num = 0
            for num, line in enumerate(_lines[1:]):
                if line[0:2] == ".." or re.search(_EMPTY_LINE, line):
                    break
            return num, _lines[0:num + 1]

        btype, block, paragraph, end = None, [], None, 0
        match = re.search(_PARAGRAPH_START, lines[line_num])
        if match:
            btype = self.block_type["paragraph"]
            paragraph = match.group()
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, paragraph), end

    def get_indent_paragraph(self, line_num, lines):
        def _get_code_block(_lines):
            num = 0
            for num, line in enumerate(_lines):
                if re.search(_EMPTY_LINE, line):
                    num -= 1
                    break
            return num, _lines[0:num + 1]

        btype, block, indent_paragraph, end = None, [], None, 0
        match = re.search(_LINE_WITH_INDENT, lines[line_num])
        if match:
            btype = self.block_type["indent_paragraph"]
            indent_paragraph = match.group()
            end, block = _get_code_block(lines[line_num:])
        return (btype, block, indent_paragraph), end

    def get_lines_with_sentence(self, text):
        def _add_linebreak(lines):
            # FIXME: more simple!
            _section_ptrn = re.compile(r"""
                ([#|*|=|\-|^|"]{2,})?  # section bar or None
                (.*?)                  # section title
                ([#|*|=|\-|^|"]{2,})   # section bar
            """, re.X)
            _lines = []
            for line in lines:
                m = re.findall(_section_ptrn, line)
                if m and isinstance(m[0], tuple):
                    # for section
                    line = "\n".join(m[0]) if m[0][0] else "\n".join(m[0][1:])
                _lines.append(u"{0}\n".format(line))
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
            if re.search(_EMPTY_LINE, line) or not match:
                lines.append(line)
            else:
                indent, text = match.groups()
                _text = self.markup_paragraph_notranslate(text)
                api, result = api_method(_text)
                lines.append(u"{0}{1}\n".format(indent, result))
        return api, lines

    def _call_for_lineblock(self, api_method, block_lines):
        api, lines = None, []
        for line in block_lines:
            match = re.match(_LINEBLOCK, line)
            if match:
                prefix, text = match.groups()
                _text = self.markup_paragraph_notranslate(text)
                api, result = api_method(_text)
                lines.append(u"{0}{1}\n".format(prefix, result))
            else:
                lines.append(line)
        return api, lines

    def _call_for_listblock(self, api_method, block_lines):
        api, lines = None, []
        for line in block_lines:
            match = re.match(_LISTBLOCK, line)
            if re.search(_EMPTY_LINE, line) or not match:
                lines.append(line)
            else:
                prefix, text = match.groups()
                _text = self.markup_paragraph_notranslate(text)
                api, result = api_method(_text)
                lines.append(u"{0}{1}\n".format(prefix, result))
        return api, lines

    def _call_for_paragraph(self, api_method, block_lines):
        text = u" ".join(t.strip() for t in block_lines)
        _text = self.markup_paragraph_notranslate(text)
        api, result = api_method(_text)
        return api, result

    def _call_for_indent_paragraph(self, api_method, block_lines):
        api, lines = None, []
        for line in block_lines:
            match = re.search(_LINE_WITH_INDENT, line)
            if match:
                prefix, text = match.groups()
                _text = self.markup_paragraph_notranslate(text)
                api, result = api_method(_text)
                lines.append(u"{0}{1}\n".format(prefix, result))
            else:
                lines.append(line)
        return api, lines

    def _call_method(self, api_method):
        in_enc, out_enc = self.encoding
        with codecs.open(self.out_file, mode="w", encoding=out_enc) as f:
            for btype, block_lines, match in self.blocks:
                print block_lines
                if btype == self.block_type["directive"]:
                    lines = block_lines
                    if re.search(_DIRECTIVE_WITH_PARAGRAPH, match):
                        ret = self._call_for_directive(
                                api_method, block_lines)
                        lines = ret[1]
                elif btype == self.block_type["lineblock"]:
                    ret = self._call_for_lineblock(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["listblock"]:
                    ret = self._call_for_listblock(api_method, block_lines)
                    lines = ret[1]
                elif btype == self.block_type["paragraph"]:
                    ret = self._call_for_paragraph(api_method, block_lines)
                    lines = self.get_lines_with_sentence(ret[1])
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
