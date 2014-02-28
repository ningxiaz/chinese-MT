#encoding=utf-8
import jieba
import jieba.posseg as pseg
import random
import nltk
from nltk.corpus import brown

class Translator:
  # def __init__(self):
     # self.model = nltk.NgramModel(1, brown.words())

  def segment(self, sentences):
    segmented = []
    for s in sentences:
      segs = list(jieba.cut(s))
      segmented.append(segs)
    return segmented
  
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
        line.append((w.word, w.flag))
      tagged.append(line)
    return tagged

  def remove_de_after_adj(self, dictionary, tagged):
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

    translated = []
    for s in tagged:
      t_sentence = []
      for i in range(len(s)):
        word = s[i][0]
        flag = s[i][1]
        # ignore words unknown to dictionary
        if word in dictionary:
          entries = dictionary[word]
          if flag in entries:
            t_flag = flag
          else: # if POS doesn't match, choose the first meaning
            t_flag = list(entries.keys())[0]
          
          if t_flag in {'v', 'n', 'r', 'rg'}:
            t_word = entries[t_flag][0][0] # for now it chooses the first one
          else:
            t_word = entries[t_flag][0]
            
          t_sentence.append([t_word, t_flag, word, flag])
            
        elif flag is 'x':
          t_sentence.append([',', flag, word, flag])
          
      translated.append(t_sentence)
    return translated

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
      if POS in {'v', 'n', 'r', 'rg'}:
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

def main():
  corpus = "../corpus/chinese.txt"
  dev_file = "../corpus/dev.txt"
  seg_file = "../corpus/segment.txt"
  dictionary_file = "../corpus/dictionary.txt"

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

  sentences = loadList(dev_file)
  tagged_tuples = translator.tag_tuple(sentences)
  tagged_tuples = translator.remove_de_after_adj(dictionary, tagged_tuples)
  translated = translator.translate(dictionary, tagged_tuples)
  dev_output = "../output/dev_output.txt"
  with open(dev_output, "w") as f:
    for s in translated:
      string_s = makeSentence([w[0] for w in s])
      f.write(string_s.encode("utf-8"))
      f.write('\n')

if __name__ == '__main__':
    main()
