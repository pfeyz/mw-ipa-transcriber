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
IPA_URL="http://www.dictionaryapi.com/api/v1/references/{0}/xml/{{word}}?key={1}".format(RESOURCE, KEYS[RESOURCE])


def get_ipa(word):
    response = urlopen(IPA_URL.format(word=urlquote(word)))
    text = response.read()
    xml = ElementTree.fromstring(text)
    entries = [e for e in xml.findall("entry")
               if re.match(r"^{0}(\[\d+\])?$".format(word), e.get('id'))]
    ipas = []
    for e in entries:
        pr = e.findall("pr")
        if pr:
            ipas.extend(pr)
    translations = []
    for ipa in ipas:
        if ipa is not None:
            if ipa.text:
                translations.extend(ipa.text.split(','))
            for i in list(ipa):
                if i.tail:
                    translations.extend([i.tail.strip(',; ')])
        else:
            alternatives = xml.findall("suggestion")
            raise WordNotFoundError(alternatives=[s.text for s in alternatives])
    if translations == []:
        raise WordNotFoundError()
    return translations

def line_to_ipa(line):
    transcribed = []
    line = line.strip()
    for word in line.split(" "):
        try:
            ipas = get_ipa(word)
            entry = u" | ".join(ipas)
            if len(ipas) > 1:
                entry = u"[ {0} ]".format(entry)
            transcribed.append(entry)
        except WordNotFoundError:
            transcribed.append(u"<<%s>>" % word)
    return transcribed

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "  You must provide input and output filenames"
        print "  Usage: mwipa infile.txt outfile.txt"
    else:
        infile, outfile = sys.argv[1:3]
        with open(infile, "r") as infh, \
                codecs.open(outfile, "w", 'utf-8') as outfh:
            lines = infh.readlines()
            length = len(lines)
            for num, line in enumerate(lines):
                print "{0}/{1}".format(num + 1, length)
                if random.random() > 0.8:
                    time.sleep(2)
                transcribed = " ".join(line_to_ipa(line))
                outfh.write(u"{0}{1}".format(transcribed, os.linesep))
