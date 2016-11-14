"""
For some unknown word or phrase, return words that describe the input based
on urbandictionary definitions.

## sample output :

[...]
homie : 1.275
just : 2.4102247191
mean : 2.48714285714
used : 2.48946582142
nope : 2.96
no : 3.1389941145


## Improvements
    - create prod-usable i/o

    - improve performance
        -- reduce # of iterations (e.g. clean_phrase is has 3 function calls
         with an iteration each. Could group them all)

    - use more logical objects. For instance, an ngram could be an object (i.e. struct)
        with current rating and references to parent sentences. Could then easily
        add parts of speech, pointers to synonyms, etc

    - add more sources: m-w.com, oed.com, wiktionary, a thesaurus
    - refine stop words based on overall distribution of words in a datasource

## Next steps
    So what now, given we have a ranked list of words?

    Assuming the system has word clusters ("no", "nuh", "*n't"):
        - determine the likelihood that the input phrase and its 1-grams correspond
            to a given cluster. For instance "naw" may correspond to a "negation" cluster
            (due to the high ranking of "no" and "nope" in the output) and "son"
            to some generic pronoun ("homie", "person").
        - From that, you should be able to induce the general "meaning", since the
            cluster arrangment "negation pronoun" should correspond to a negative response


"""


import math, re
import requests


def get_response_set(phrase):
    """ Returns set()

        @type - str
        @param - all sequential combinations of words from 0 to n.
                 e.g. "Hey you" = set(["Hey", "you", "Hey you"])
    """

    response_set = set()
    split_phrase = phrase.split()
    for i in range(0, len(split_phrase) + 1):
        for j in range(i, len(split_phrase) + 1):
            if (split_phrase[i : j]):
                response_set.add(' '.join(split_phrase[i : j]))
    return response_set


def ask_urban_dictionary(term):
    """ Returns list of tuples : ("definition", float(positive ratings), float(negative ratings))

        @type - str
        @param - a word for whichto retrieve definitions from urbandictionary.com
    """
    url = "http://api.urbandictionary.com/v0/define?term={}"
    def_words = {}

    j = requests.get(url.format(term))
    j = j.json()
    defs = [(el["definition"], el["thumbs_up"], el["thumbs_down"]) for el in j["list"]]
    return defs


def get_stop_words():
    """ read in stop_words.txt or get cached value to save on I/O """
    global stop_words
    try:
        return stop_words
    except NameError:
        f = open("./stop_words.txt")
        f = f.read()
        stop_words = set(f.split("\n"))
        return stop_words

def remove_stop_words(word_list):
    """ remove stop words from a string """
    stop_words = get_stop_words()
    words = [w for w in word_list if w not in stop_words]
    return words

def get_definition_rating(thumbs_up, thumbs_down):
    """ rank a whole definition based on community feedback.
        divided by 100, which is a lazy way to make sure the definition rankings don't
        blow out the word frequency rankings
    """
    r = thumbs_up - thumbs_down
    return r/100.0

def get_word_frequency(word_list):
    """ for each word, get the probability a a given word is X """
    sl = len(word_list)
    freqs = {}
    for w in word_list:
        try:
            freqs[w] += 1
        except KeyError:
            freqs[w] = 1

    d_w = len(freqs.keys()) * 1.0
    for key in freqs:
        freqs[key] = (freqs[key]/d_w)

    return freqs

def clean_phrase(word_list):
    """ make lowercase, rm non-alphanumeric, remove stop words """
    word_list = [word.lower() for word in word_list]
    word_list = [re.sub("[^a-zA-Z0-9]+", "", word) for word in word_list]
    word_list = remove_stop_words(word_list)
    return word_list

def process(phrase):
    response_set = get_response_set(phrase)
    ranking = {}

    for ngram in response_set:
        defs = ask_urban_dictionary(ngram)

        for defn_tuple in defs:
            def_ranking = get_definition_rating(defn_tuple[1], defn_tuple[2])

            defn = defn_tuple[0].split()
            defn = clean_phrase(defn)
            defn_dict = get_word_frequency(defn)

            for word in defn_dict:
                try:
                    ranking[word] += (defn_dict[word] * def_ranking)
                except KeyError:
                    ranking[word] = (defn_dict[word] * def_ranking)
    return ranking

if __name__ == "__main__":
    rankings = process("naw son")

    for key in sorted(rankings, key=rankings.get):
        print "{} : {}".format(key, rankings[key])
