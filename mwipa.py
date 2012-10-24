import codecs
import os
import sys
import random
import re
import time
import xml.etree.cElementTree as ElementTree
from urllib import quote as urlquote
from urllib2 import urlopen


class WordNotFoundError(KeyError):
    def __init__(self, alternatives=None, *args, **kwargs):
        KeyError.__init__(self, *args, **kwargs)
        self.alternatives = alternatives

RESOURCE = "learners"
KEYS = {"learners": "",
        "collegiate": ""}
MW_URL="http://www.dictionaryapi.com/api/v1/references/{0}/xml/{{word}}?key={1}".format(RESOURCE, KEYS[RESOURCE])

def format_unknown(word):
    " Formats `word` to indicate that word has not been translated. "
    return u"<<%s>>" % word

def format_alternatives(ipas):
    """ Returns a string joining the strings in `ipas`, indicating that they are
    multiple alternative translations.

    """

    alts = u" | ".join(ipas)
    alts = u"[ {0} ]".format(alts)
    return alts

def get_mw_nodes(root, tag, word):
    """ Returns `tag` sub-nodes found for all entry nodes that match `word`
    exactly in `root`.

    """

    # tag id is either "word" or "word[#]" where # is an actual number
    entries = [e for e in root.findall("entry")
               if re.match(r"^{0}(\[\d+\])?$".format(word), e.get('id'))]
    return [pr for e in entries
            for pr in e.findall(tag) if pr is not None]

def query_mw(word):
    response = urlopen(MW_URL.format(word=urlquote(word)))
    text = response.read()
    xml = ElementTree.fromstring(text)
    return xml

def get_pos(word, cache={}):
    if word in cache:
        return cache[word]
    xml = query_mw(word)
    pos = get_mw_nodes(xml, "fl", word)
    if pos == []:
        alternatives = xml.findall("suggestion")
        raise WordNotFoundError(alternatives=[s.text for s in alternatives])
    return [p.text for p in pos]

def get_ipa(word, cache={}):
    """ Queries Merriam Webster for `word`. Caches results.

    Returns a list of IPA translations. Throws WorNotFoundError if no
    translations are found, possibly with a list of similar words MW suggested.

    Results are cached.

    """

    if word in cache:
        return cache[word]
    xml = query_mw(word)
    ipas = get_mw_nodes(xml, "pr", word)
    if ipas == []:
        alternatives = xml.findall("suggestion")
        raise WordNotFoundError(alternatives=[s.text for s in alternatives])
    translations = []
    for ipa in ipas:
        if ipa.text:
            translations.extend(ipa.text.split(','))
        for i in list(ipa):
            if i.tail:
                translations.extend([i.tail.strip(',; ')])
    cache[word] = translations
    return translations

def translate_line(line, translator):
    translated = []
    for word in line.split(" "):
        try:
            ts = translator(word)
        except WordNotFoundError:
            translated.append(format_unknown(word))
            continue
        if len(ts) > 1:
            translated.append(format_alternatives(ts))
        else:
            translated.append(ts[0])
    return translated

def main(infile, outfile):
    with open(infile, "r") as infh, \
            codecs.open(outfile, "w", 'utf-8') as outfh:
        lines = infh.readlines()
        length = len(lines)
        for num, line in enumerate(lines):
            line = line.strip()
            print "{0}/{1}".format(num + 1, length)
            if random.random() > 0.8:
                time.sleep(2)
            x = translate_line(line, get_pos)
            transcribed = " ".join(x)
            print transcribed
            outfh.write(u"{0}\t{1}{2}".format(line, transcribed, os.linesep))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "  You must provide input and output filenames"
        print "  Usage: mwipa infile.txt outfile.txt"
    else:
        infile, outfile = sys.argv[1:3]
        main(infile, outfile)
