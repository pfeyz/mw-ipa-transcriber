Merriam-Webster IPA Transcriber

A simple script for querying Merriam-Webster's Dictionary API for IPA
transcriptions. Also includes part-of-speech functionality. To use it you'll
need to get API keys from `Merriam-Webster's Developer Center`_ and populate the
KEYS dictionary with them. The script is written to work with the collegiate and
learner's dictionary, but you should know that it looks like the collegiate
dictionary uses it's own non-ipa_ pronunciation notation.

Use of the Merriam Webster Dictionary API is subject to their `terms of
service`_.

.. _`Merriam-Webster's Developer Center`: http://www.dictionaryapi.com/
.. _`terms of service`: http://www.dictionaryapi.com/info/terms-of-service.htm
.. _`non-ipa`: http://en.wikipedia.org/wiki/Merriam-Webster#Pronunciation_guides

::

  >>> from mwipa import get_ipa
  >>> for ipa in get_ipa("tomato"):
  ...     print ipa
  ...
  təˈmeɪtoʊ
  təˈmɑ:təʊ

The script can also be used as a command line program for batch transcription.

::

  $ python mwipa.py -h
  usage: mwipa.py [-h] (-i | -p) infile outfile

  Query merriam-webster.com

  positional arguments:
    infile      Text file without punctuation to use as input
    outfile     Output file to write tab-seperated data to

  optional arguments:
    -h, --help  show this help message and exit
    -i, --ipa   Retrive IPA translations
    -p, --pos   Retrieve POS information

For example,

::

  $ python mwipa.py -i in.txt out.csv
  1/2
  2/2

Will result in the following "out.csv" given this "in.txt". Words unable to be
transcribed are indicated like <<this>> and words with alternative transcriptions are [ listed | like | this ] .

::

  <in.txt>
  lemmings do not engage in mass suicidal dives off cliffs when migrating
  this misconception was popularized by the Disney film White wilderness

::

  <out.csv>
  lemmings do not engage in mass suicidal dives off cliffs when migrating	<<lemmings>> [ ˈdu: | ˈdoʊ ] ˈnɑ:t ɪnˈgeɪʤ [ ˈɪn | ən | ˈɪn | ˈɪn | ˈɪn ] ˈmæs ˌsu:wəˈsaɪdl̟ <<dives>> ˈɑ:f <<cliffs>> ˈwɛn <<migrating>>
  this misconception was popularized by the Disney film White wilderness	[ ˈðɪs | ðəs | ˈðɪs ] ˌmɪskənˈsɛpʃən <<was>> <<popularized>> [ ˈbaɪ | bə | ˈbaɪ ] [ ðə | ði | ˈði: ] <<Disney>> ˈfɪlm <<White>> ˈwɪldɚnəs

As you can see, inflected forms aren't currently recognized.
