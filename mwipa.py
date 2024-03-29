import argparse
import codecs
import os
import re
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
    """ Queries Merriam Webster POS listings for `word`.

    Returns a list of POS entries. Throws WordNotFoundError if no POS are found,
    possibly with a list of similar words MW suggested.

    Results are cached.

    """

    if word in cache:
        return cache[word]
    xml = query_mw(word)
    pos = get_mw_nodes(xml, "fl", word)
    if pos == []:
        alternatives = xml.findall("suggestion")
        raise WordNotFoundError(alternatives=[s.text for s in alternatives])
    pos_text = [p.text for p in pos]
    cache[word] = pos_text
    return pos_text

def get_ipa(word, cache={}):
    """ Gets Merriam Webster IPA translation for `word`.

    Returns a list of POS. Throws WordNotFoundError if no translations are
    found, possibly with a list of similar words MW suggested.

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
            translations.extend([part.strip() for part in ipa.text.split(',')
                                 if part.strip()])
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

def main(args):
    if not KEYS[RESOURCE]:
        raise Exception("No API Keys supplied")
    with open(args.infile, "r") as infh, \
            codecs.open(args.outfile, "w", 'utf-8') as outfh:
        if args.ipa:
            translator = get_ipa
        else:
            translator = get_pos
        lines = infh.readlines()
        length = len(lines)
        for num, line in enumerate(lines):
            line = line.strip()
            print "{0}/{1}".format(num + 1, length)
            transcribed = " ".join(translate_line(line, translator))
            outfh.write(u"{0}\t{1}{2}".format(line, transcribed, os.linesep))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("Query merriam-webster.com "
                                                  "for IPA or POS data"))
    parser.add_argument('infile',
                        help='Text file without punctuation to use as input')
    parser.add_argument('outfile',
                        help='Output file to write tab-seperated data to')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-i', '--ipa', action='store_true',
                        help="Retrive IPA translations")
    action.add_argument('-p', '--pos', action='store_true',
                        help="Retrieve POS information")
    args = parser.parse_args()
    main(args)
