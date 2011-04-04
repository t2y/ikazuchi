# -*- coding: utf-8 -*-

try:
    import vim
except ImportError:
    print "call ':pyfile raimei' from vim"

import izuchi
import re
import sys
import threading
from os.path import splitext

_SENTENCE_PATTERN = {
    "en": unicode(r"[\.|\?|!|:][ |$]+", "utf-8"),
    "ja": unicode(r"[。|．|？|！]", "utf-8"),
}

_END_OF_SENTENCE = unicode(r"[\.|\?|:|!|。|．|？|！]$", "utf-8")

def _to_unicode(seq, enc):
    return [unicode(i, enc) for i in seq]

def _to_encode(seq, enc):
    return [i.encode(enc) for i in seq]

def get_vim_variables():
    # settings from VimScript(.vimrc)
    try:
        api_name = vim.eval("raimei_api")
        lang_from = vim.eval("raimei_from")
        lang_to = vim.eval("raimei_to")
        enc = vim.eval("&enc")
    except vim.error:
        #  vim.error is String Exception
        print "Set enc, raimei_api, raimei_from, raimei_to variables!"
        raise
    return api_name, lang_from, lang_to, enc

def remove_imcomplete_line(lines, start, enc):
    prev = vim.current.buffer[start - 1:start]
    if prev and prev[0]:
        if not re.search(_END_OF_SENTENCE, unicode(prev[0].rstrip(), enc)):
            # remove first line if previous line is not end of a sentence
            lines = lines[1:]
    return lines

def get_lines_with_sentence(start, end, enc):
    _buffer = vim.current.buffer[start:end]
    text = u" ".join(unicode(t.strip(), enc) for t in _buffer)
    text += u" "  # FIXME: pattern matching for end with "."

    # get lines for each single sentence
    lines = []
    flags = re.MULTILINE | re.UNICODE
    base_ptrn = _SENTENCE_PATTERN.get(vim.eval("raimei_from")) or \
                _SENTENCE_PATTERN["en"]
    sentence_num = len(re.findall(base_ptrn, text, flags))
    if sentence_num > 0:
        ptrn = u"(.*{0})".format(base_ptrn) * sentence_num
        match = re.findall(ptrn, text, flags)
        # format lines
        if match:
            if isinstance(match[0], tuple):
                lines = remove_imcomplete_line(match[0], start, enc)
                lines = [line.strip().rstrip() for line in lines]
            else:
                lines = [match[0].strip().rstrip()]
    return lines

def get_target_lines(start, end, enc):
    lines = get_lines_with_sentence(start, end, enc)
    if not lines:
        # with lines "as is"
        lines = _to_unicode(vim.current.buffer[start:end], enc)
    return lines

def call_api_with_multithread(api_method, target_lines):
    def worker(line, results, i):
        results[i] = api_method(line)

    results = []
    for i, line in enumerate(target_lines):
        results.append(None)
        t = threading.Thread(target=worker, args=(line, results, i))
        t.start()
    # waiting for threads to complete
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    return results

def translate_with_range(translator, enc):
    start = vim.current.range.start
    end = vim.current.range.end + 1
    target_lines = get_target_lines(start, end, enc)
    # call translate API with multithread
    ret = call_api_with_multithread(translator.translate, target_lines)
    api = ret[0][0]
    # previous and last empty lines are just for look and feel
    translated = ["", ] + [r.encode(enc) for _, r in ret] + ["", ]
    # add translated text into vim
    vim.current.buffer.append(translated, end)
    vim.command("let raimei_target_lines={0}".format(
                _to_encode(target_lines, enc)))
    print "Translated by {0}".format(api.encode(enc))

def translate(api_name, lang_from, lang_to, enc):
    t = izuchi.translator.TRANSLATE_API[api_name](lang_from, lang_to, None)
    return translate_with_range(t, enc)

def comment_out_original_lines():
    start = vim.current.range.start + 1
    end = vim.current.range.end + 2
    vim.current.buffer.append("..", start - 1)
    for num, line in enumerate(vim.current.buffer[start:end]):
        vim.current.buffer[start + num] = "{0}{1}".format(" " * 4, line)

def main():
    try:
        vim_vars = get_vim_variables()
        translate(*vim_vars)
        ext = splitext(vim.current.buffer.name)[1][1:]
        if ext == "rst":
            comment_out_original_lines()
    except Exception as err:
        print err.message
        return

if __name__ == "__main__":
    main()
