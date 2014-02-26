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

def main():
  corpus = "../corpus/chinese.txt"
  seg_file = "../corpus/segment.txt"

  bl_translator = BaselineTranslator()
  sentences = loadList(corpus)

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
