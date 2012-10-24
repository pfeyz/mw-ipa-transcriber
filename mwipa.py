import codecs
import os
import sys
import random
import time
import xml.etree.cElementTree as ElementTree
from urllib import quote as urlquote
from urllib2 import urlopen


class WordNotFoundError(KeyError):
    def __init__(self, alternatives, *args, **kwargs):
        KeyError.__init__(self, *args, **kwargs)
        self.alternatives = alternatives

API_KEY = ""
IPA_URL="http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{{word}}?key={0}".format(API_KEY)

def get_ipa(word):
    response = urlopen(IPA_URL.format(word=urlquote(word)))
    text = response.read()
    xml = ElementTree.fromstring(text)
    ipa = xml.find("*/pr")
    if ipa is not None:
        return ipa.text
    else:
        alternatives = xml.findall("suggestion")
        raise WordNotFoundError(alternatives=[s.text for s in alternatives])

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
                if random.random() > 0.7:
                    time.sleep(2)
                for word in [w.strip() for w in line.split(" ")]:
                    try:
                        outfh.write(u"{0}, {1}{2}".format(word, get_ipa(word),
                                                          os.linesep))
                    except WordNotFoundError, e:
                        outfh.write(u"{0}, {1}".format(
                            word, u"No results for {0}. Maybe try {1}{2}".format(
                                word,
                                ", ".join(e.alternatives),
                                os.linesep)))
