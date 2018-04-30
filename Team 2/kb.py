import re
import json
import itertools

ACCEPT_THRESHOLD = 0.32


class Rejector:
    def __init__(self, kb='rejects.json'):
        self.kb_file = kb
        self.rejects = open(self.kb_file)
        self.alphabets = json.load(self.rejects) or dict()

    def add(self, words):
        """
        Add word to the reject list. All words are indexed
        by their first character.
        """
        for word in words.strip().split(' '):
            self.alphabets[word.strip()[0]].extend(word.strip().split(' '))
            self.alphabets[word.strip()[0]] = list(
                set(self.alphabets[word.strip()[0]]))

    def close(self):
        with open(self.kb_file, 'w') as kb_file:
            json.dump(self.alphabets, kb_file, indent='\t')

    def process(self, dirty_string):
        """
        Strip all input of undesirable portions, in listed order:
        1. All punctuations
        2. All unterminated braces
        3. All extra spacing
        """
        dirty_string = re.sub(r"\(.*\)", "", dirty_string)
        dirty_string = re.sub(
            r"[,.\{.*\}\[.*\]\'\"\:\;\-\\/&#\^_\-\+]*[0-9]*",
            "",
            dirty_string)
        dirty_string = re.sub(r"\(.*", "", dirty_string)
        dirty_string = re.sub(r".*\)", "", dirty_string)
        dirty_string = re.sub(r"[ ]+", " ", dirty_string).strip('\n').strip()
        rejected_words = list()
        input_words = dirty_string.split(' ')
        for word in input_words:
            if word == '':
                return ''
            rejected_words.extend(self.alphabets[word[0].upper()])

        for product in itertools.product(rejected_words, input_words):
            # match any of the rejected words selected in the input string
            if product[0].upper() == product[1].upper():
                rejector.add(product[0])
                try:
                    input_words.remove(product[1])
                except ValueError:
                    pass  # Exact word was not found

        if len(input_words) == 0:  # Input was completely rejected, return empty string
            return ''

        #clean_string = functools.reduce(lambda s,a: s+ ' ' + a, input_words)
        # Rebuild string from clean word list

        clean_string = " ".join(input_words)
        return clean_string


class Acceptor:
    def __init__(self, kb="condensed_file.json"):
        self.kb_file = kb
        self.accepted = open(self.kb_file)
        self.alphabets = json.load(self.accepted) or dict()

    def add(self, word):
        try:
            self.alphabets[word.strip().upper()[0]].append(
                word.strip().upper())
        except KeyError:
            self.alphabets[word.strip().upper()[0]] = list(
                word.strip().upper())
        finally:
            self.alphabets[word.strip().upper()[0]] = list(
                set(self.alphabets[word.strip().upper()[0]]))

    def close(self):
        with open(self.kb_file, 'w') as kb_file:
            json.dump(self.alphabets, kb_file, indent='\t')

    def process(self, dirty_string):
        clean_string = rejector.process(dirty_string)
        parts = clean_string.split(' ')
        parts_matched = 0
        for word in parts:
            match_candidates = self.alphabets[word.strip().upper()[0]]
            word = word.strip().upper()
            if word in match_candidates:
                parts_matched += 1
            else:
                rejector.add(word)

        if parts_matched / len(parts) > ACCEPT_THRESHOLD:
            acceptor.add(clean_string)


class Matcher:
    def close(self):
        with open(self.kb_file, 'w') as kb_file:
            json.dump(self.hashes, kb_file, indent='\t')

    def __init__(self, kb="matches.json"):
        self.kb_file = kb
        self.matched = open(self.kb_file)
        self.hashes = json.load(self.matched)

    def add(self, title, match):
        main_key = self.hashes[title.upper()[0]]
        try:
            if title.upper()[0] == match[0].upper():
                list(set(main_key[title.upper()]["matches"])).append(
                    match.upper())

        except KeyError:
            main_key[title.upper()] = dict({"matches": [match.upper()]})

    def match(self, match_query):
        keys = self.hashes[match_query[0]]

        for key in keys.keys():
            if match_query.upper() in keys[key].get("matches"):
                return key
        return None


def end():
    matcher.close()
    rejector.close()
    acceptor.close()


matcher = Matcher()
rejector = Rejector()
acceptor = Acceptor()
