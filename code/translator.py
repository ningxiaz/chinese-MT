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

  Ex: dict[word][index] = [translation, POS]
      Use dict[word][index][0] to access translation.
      Use dict[word][index][1] to access corresponding POS. """

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
  seg_file = "../corpus/segment.txt"
  dictionary_file = "../corpus/dictionary.txt"

  bl_translator = BaselineTranslator()
  sentences = loadList(corpus)
  dictionary = loadDictionary(dictionary_file)

  segmented = bl_translator.segment(sentences)
  with open(seg_file, "w") as f:
    for s in segmented:
      string_s = " ".join(s)
      f.write(string_s.encode("utf-8"))
      f.write('\n')
  f.close()

  dev = "../corpus/dev.txt"
  output_tagged = "../corpus/dev_tagged.txt"
  dev_sentences = loadList(dev)
  dev_tagged = bl_translator.tag(dev_sentences)
  with open(output_tagged, "w") as f:
    for s in dev_tagged:
      string_s = " ".join(s)
      f.write(string_s.encode("utf-8"))
      f.write('\n')
  f.close()

if __name__ == '__main__':
    main()
