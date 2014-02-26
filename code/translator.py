#encoding=utf-8
import jieba

class BaselineTranslator:
  # def __init__(self, sentences):
  #   self.sentences = sentences

  def segment(self, sentences):
    segmented = []
    for s in sentences:
      segs = list(jieba.cut(s))
      segmented.append(segs)
    return segmented

def loadList(file_name):
    """Loads text files as lists of lines. """
    with open(file_name) as f:
        l = [line.decode("utf-8").strip() for line in f]
    return l

def main():
  corpus = "../corpus/chinese.txt"
  seg_file = "../corpus/segment.txt"

  bl_translator = BaselineTranslator()
  dev_sentences = loadList(corpus)

  segmented = bl_translator.segment(dev_sentences)
  with open(seg_file, "w") as f:
    for s in segmented:
      string_s = " ".join(s)
      f.write(string_s.encode("utf-8"))
      f.write('\n')

if __name__ == '__main__':
    main()
