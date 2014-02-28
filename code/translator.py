#encoding=utf-8
import jieba
import jieba.posseg as pseg
import random
import math
import nltk
from nltk.corpus import brown

class Translator:
  def __init__(self):
     self.model = nltk.NgramModel(1, brown.words())

  def segment(self, sentences):
    segmented = []
    for s in sentences:
      segs = list(jieba.cut(s))
      segmented.append(segs)
    return segmented
  
  def transfer(self, tag):
    pass

  def tag(self, sentences):
    tagged = []
    for s in sentences:
      words = pseg.cut(s)
      line = []
      for w in words:
        line.append(w.word + "/" + w.flag)
      tagged.append(line)
    return tagged

  def tag_tuple(self, sentences):
    tagged = []
    for s in sentences:
      words = pseg.cut(s)
      line = []
      for w in words:
        if w.flag is 'l':
          line.append((w.word, 'n'))
        elif w.flag is 'uj':
          line.append((w.word, 'p'))
        else:
          line.append((w.word, w.flag))
      tagged.append(line)
    return tagged

  def remove_le(self, tagged):
    for s in tagged:
      to_delete = []
      for i in range(len(s)):
        if s[i][0] == u"了":
          to_delete.append(i)
      for i in reversed(to_delete):
        del s[i]

  def come_and_go_correction(self, tagged):
    """
    In Chinese, "来" and "去", if in front of verbs, they mean "to"
    """
    for s in tagged:
      for i in range(len(s)):
        if s[i][0] == u'来' or s[i][0] == u'去':
          if s[i][1] is 'v' and i + 1 < len(s) and s[i+1][1] is 'v':
            s[i] = (s[i][0], 'p')

  def remove_de_after_adj(self, dictionary, tagged):
    """
    In Chinese, whenever "的" follows a word, they together may make an adjective
    So, "的" doesn't mean anything in this case.
    """
    new_tagged = []
    for s in tagged:
      new_s = []
      for i in range(len(s)):
        w = s[i]
        if w[0] == u'的' and i > 0:
          new_w = s[i - 1][0] + w[0]
          if new_w in dictionary:
            # print new_w.encode("utf-8")
            new_s[-1] = (new_w, 'a')
          elif i + 1 < len(s) and s[i+1][1] is 'x':
            pass
          else:
            new_s.append(w)
        else:
          new_s.append(w)
      new_tagged.append(new_s)
    return new_tagged

  def remove_unnecessary_character(self, tagged):
    """
    In Chinese, "当...时" means When...
    So, "时" is not necessary
    """
    for s in tagged:
      to_delete = []
      for i in range(len(s)):
        if s[i][0] == u"当" and s[i][1] is 't':
          for j in range(i, len(s)):
            if s[j][0] == u"时":
              to_delete.append(j)
            if s[j][1] is 'x':
              break
      for i in reversed(to_delete):
        del s[i]

  def preposition_reorder(self, tagged):
    for s in tagged:
      zai = []
      for i in range(len(s)):
        if s[i][1] is 'f' and i > 0:
          if s[i - 1][1] is 'n':
            w = (s[i][0], 'p')
            s[i] = s[i - 1]
            s[i - 1] = w
            if i > 1 and s[i - 2][0] == u'在':
              zai.append(i - 2)
      for i in reversed(zai):
        del s[i]

  def of_reorder(self, tagged):
    for s in tagged:
      to_delete = []
      for i in range(len(s)):
        if s[i][0] == u'的':
          if i > 0 and i + 1 < len(s):
            if s[i - 1][1] is 'n' and s[i + 1][1] is 'n':
              w = s[i - 1]
              s[i - 1] = s[i + 1]
              s[i + 1] = w
              if i - 1 > 0 and s[i - 2][1] is 'p':
                w = s[i]
                s[i] = s[i - 2]
                s[i - 2] = w
                to_delete.append(i - 2)
      for i in reversed(to_delete):
        del s[i]

  def translate(self, dictionary, tagged):
    """
    Translate word by word by looking up in the dictionary

    First we match the POS tag, if no match, pick a random one.
    TODO: use language model to choose the most likely one in English.

    TODO: (now just pick the first one)
    For special cases:
      nouns:
      pronoun: (maybe look for verb before it)
      verbs: (look for past tense signs, and NERs talked about)
    """

    """
    Helper function to determine the verb form
    t_sentence: the translated sentence
    """
    def verb_form(forms, t_sentence):
      # first find the nearest pronoun before this verb
      return 

    def determineNoun(word):
      plurality = "singular"
      person = 3
      #Check for 们
      if u'\u4eec' in word:
        plurality = "plural"
      #Check for 你 or 我
      if u'\u4f60' in word:
        person = 2
      elif u'\u6211' in word:
        person = 1

      return [plurality, person]


    translated = []
    for s in tagged:
      t_sentence = []
      # Default plurality is singular
      prev_noun_plurality = "singular"
      # Default person without noun is 2nd
      prev_noun_person = 2
      nouns_seen = 0
      for i in range(len(s)):
        word = s[i][0]
        flag = s[i][1]
        # ignore words unknown to dictionary
        if word in dictionary:
          candidates = []
          entries = dictionary[word]
          if flag in entries:
            for translation in entries[flag]:
              candidates.append([translation, flag])
          else:
            for POS in list(entries.keys()):
              for translation in entries[POS]:
                candidates.append([translation, POS])


          # Choose the best based on the language model
          best_translation = ""
          best_POS = ""
          best_score = float('-inf')

          for candidate in candidates:
              translation = candidate[0]
              POS = candidate[1]
              translation_score = 0.0
              for tense in translation:
                tense_score = self.model.prob(tense, [])
                #Handle bug in nltk.ngrams. It returns 0.022011... when word isn't found
                if tense_score > 0.022011 and tense_score < 0.022012:
                  tense_score = 0
                translation_score += tense_score
              # Take average probability of tenses
              if translation_score > best_score:
                best_translation = translation
                best_POS = POS
                best_score = translation_score


          t_flag = best_POS
          # Determine if plural is true or false
          if t_flag in {'n','r','nr'}:
            if t_flag == 'nr':
              prev_noun_plurality = "singular"
              prev_noun_person = 3
            else:
              prev_noun = determineNoun(word)
              prev_noun_plurality = prev_noun[0]
              prev_noun_person = prev_noun[1]
            nouns_seen = nouns_seen + 1
          if t_flag == 'n':
            if prev_noun_plurality == 'singular':
              t_word = best_translation[0]
            else:
              t_word = best_translation[1]
          elif t_flag == 'r':
            if nouns_seen == 1:
              t_word = best_translation[0]
            elif i+1 < len(s) and s[i+1][0] == u'\u7684':
              # Checked for 的
              t_word = best_translation[2]
            else:
              t_word = best_translation[1]
          elif t_flag == 'v':
            is_verb = ("be" in best_translation[0])
            can_verb = ("can" in best_translation[0])
            if is_verb:
              if prev_noun_plurality == "singular" and prev_noun_person == 1:
                t_word = best_translation[1]
              elif prev_noun_plurality == "singular" and prev_noun_person == 3:
                t_word = best_translation[2]
              else:
                t_word = best_translation[3]
            elif can_verb:
              t_word = best_translation[0]
            else:
              if prev_noun_person == 3 and prev_noun_plurality == "singular":
                t_word = best_translation[1]
              else:
                t_word = best_translation[0]

          else:
            t_word = best_translation[0]
          t_sentence.append([t_word, t_flag, word, flag])
            
        elif flag is 'x':
          t_sentence.append([',', flag, word, flag])
      translated.append(t_sentence)
    return translated

  def modal_verbs_check(self, dictionary, translated):
    modal_verbs = {'can', 'could', 'should', 'must', 'may', 'might', 'to', 'shall', 'will', 'would'}
    check_after = 8
    for s in translated:
      for i in range(len(s)):
        if s[i][0] in modal_verbs:
          for j in range(i + 1, min(i + check_after, len(s))):
            if s[j][1] is 'v':
              chinese = s[j][2]
              for candidates in dictionary[chinese]['v']:
                if s[j][0] in candidates:
                  s[j][0] = candidates[0] # must be original form

  def nouns_check(self, dictionary, translated):
    plural_indications = {'many', 'these', 'those', 'few', 'several', 'multiple'}
    for s in translated:
      for i in range(len(s)):
        if s[i][0] in plural_indications and i + 1 < len(s):
          if s[i + 1][1] is 'n':
            chinese = s[i + 1][2]
            for candidates in dictionary[chinese]['n']:
              if s[i + 1][0] in candidates:
                s[i + 1][0] = candidates[1] # must be plurals

def loadList(file_name):
    """Loads text files as lists of lines. """
    with open(file_name) as f:
        l = [line.decode("utf-8").strip() for line in f]
    return l

def loadDictionary(file_name):
  """
  Structure of entries in file:
    general --> CHINESE:POS=TRANSLATION,POS=TRANSLATION
   
   Special case entries:
    nouns --> n=singular|plural 
    pronoun --> r=subject|object|possessive
    verbs --> v=present|present_plus_s|past|present_participle|past_participle
        note: present participle example = "he is -->eating<--"
        note: past participle example = "you have -->eaten<--"

  Ex: dict[word][POS] = [translation1, translation2,...]
      If POS is 'r', translation will be a list of three:
          translation = [subject_form, object_form, possessive_form]
      If POS is 'n', translation will be a list of two:
          translation = [singular, plural]
      If POS is 'v', translation will be a list of five:
          translation = [present, present_with_s, past, present_participle, past_participle]
      Else, translation will be a list of one:
          translation = [translation]

      Special Cases: "is" verbs and "can"
               "be|am|is|are|was|were|being|been" and "can|can|could"
  """

  dict = {}
  lines = loadList(file_name)
  for line in lines:
    line_split = line.split(':')
    word = line_split[0]
    entries = line_split[1].split(',')
    dict[word] = {}
    for entry in entries:
      entry_split = entry.split('=')
      POS = entry_split[0]
      translation = entry_split[1]
      if POS not in dict[word]:
        dict[word][POS] = []
      translation = translation.split('|')
      dict[word][POS].append(translation)

  return dict

def makeSentence(wordlist):
  """
  Take a list of words, detect comma and delete extra spaces before it,
  change the last comma to period, and return the final sentence.
  """
  if wordlist[-1] is ',':
    wordlist[-1] = '.'
  sentence = wordlist[0].capitalize()
  for i in range(1, len(wordlist)):
    w = wordlist[i]
    if w is ',' or w is '.':
      sentence += w
    else:
      sentence += (' '+w)
  return sentence

def write_translations(translated, output):
  with open(output, "w") as f:
    for s in translated:
      string_s = makeSentence([w[0] for w in s])
      f.write(string_s.encode("utf-8"))
      f.write('\n')

def main():
  corpus = "../corpus/chinese.txt"
  dev_file = "../corpus/dev.txt"
  seg_file = "../corpus/segment.txt"
  dictionary_file = "../corpus/dictionary.txt"

  test_file = "../corpus/test.txt"

  translator = Translator()
  sentences = loadList(corpus)
  dictionary = loadDictionary(dictionary_file)

  # segmented = bl_translator.segment(sentences)
  # with open(seg_file, "w") as f:
  #   for s in segmented:
  #     string_s = " ".join(s)
  #     f.write(string_s.encode("utf-8"))
  #     f.write('\n')

  dev = "../corpus/dev.txt"
  output_tagged = "../corpus/dev_tagged.txt"
  dev_sentences = loadList(dev)
  dev_tagged = translator.tag(dev_sentences)
  with open(output_tagged, "w") as f:
    for s in dev_tagged:
      string_s = " ".join(s)
      f.write(string_s.encode("utf-8"))
      f.write('\n')

  sentences = loadList(test_file)
  tagged_tuples = translator.tag_tuple(sentences)
  translator.remove_le(tagged_tuples)
  translator.come_and_go_correction(tagged_tuples)
  tagged_tuples = translator.remove_de_after_adj(dictionary, tagged_tuples)
  translator.remove_unnecessary_character(tagged_tuples)
  translator.preposition_reorder(tagged_tuples)
  translator.of_reorder(tagged_tuples)
  translated = translator.translate(dictionary, tagged_tuples)
  translator.modal_verbs_check(dictionary, translated)
  translator.nouns_check(dictionary, translated)
  dev_output = "../output/test_output.txt"

  write_translations(translated, dev_output)

if __name__ == '__main__':
    main()
