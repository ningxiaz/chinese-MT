#encoding=utf-8
import jieba
import jieba.posseg as pseg

class BaselineTranslator:
  # def __init__(self, sentences):
  #   self.sentences = sentences

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

  def translate(self, dictionary, tagged):
    translated = []
    for s in tagged:
      t_sentence = []
      for word, flag in s:
        # ignore words unknown to dictionary
        if word in dictionary:
          entries = dictionary[word]
          tag_found = False
          for e in entries:
            if e[1] is flag:
              tag_found = True
              t_word = e[0]
              t_flag = flag

          # if POS tag not found, use the first translation
          if not tag_found:
            t_word = entries[0][0]
            t_flag = entries[0][1]

        # elif word is u"\u002C":
        #   t_word = ','
        # elif word is u"\u002E":
        #   t_word = '.'
          t_sentence.append((t_word, t_flag))
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
      if POS == 'r' or POS == 'n' or POS == 'v':
        translation = translation.split('|')
      dict[word][POS].append(translation)

  return dict

def main():
  corpus = "../corpus/chinese.txt"
  dev_file = "../corpus/dev.txt"
  seg_file = "../corpus/segment.txt"
  dictionary_file = "../corpus/dictionary.txt"

  bl_translator = BaselineTranslator()
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
  dev_tagged = bl_translator.tag(dev_sentences)
  with open(output_tagged, "w") as f:
    for s in dev_tagged:
      string_s = " ".join(s)
      f.write(string_s.encode("utf-8"))
      f.write('\n')

  sentences = loadList(dev_file)
  tagged_tuples = bl_translator.tag_tuple(sentences)
  translated = bl_translator.translate(dictionary, tagged_tuples)
  dev_output = "../output/dev_output.txt"
  with open(dev_output, "w") as f:
    for s in translated:
      string_s = " ".join([w[0] for w in s])
      f.write(string_s.encode("utf-8"))
      f.write('\n')


if __name__ == '__main__':
    main()
