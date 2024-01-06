import docx
import os
from docx.shared import Pt, RGBColor

def replace_doc(document):
    doc = docx.Document(document)
    text = []
    for paragraph in doc.paragraphs:
        for str_rep in get_replace_str():
            if str_rep[1] == '' and paragraph.text.find(str_rep[0]) != -1:
                paragraph.text = None
                # paragraph.text = paragraph.text.replace(str_rep[0], '')
                # paragraph.style.font.name = 'Times New Roman'
                # paragraph.style.font.size = Pt(9)
            if paragraph.text.find(str_rep[0]) != -1:
                print(paragraph.text)
                paragraph.text = paragraph.text.replace(str_rep[0], str_rep[1])
                paragraph.style.font.name = 'Times New Roman'
                paragraph.style.font.size = Pt(14)
                print(paragraph.text)
    doc.save(document)


def get_files():
    files = []
    file_dir = os.listdir(path='word_doc')
    for file in file_dir:
        files.append(f"{os.path.abspath('word_doc')}/{file}")
    return files

def get_replace_str():
    replace_str = []
    with open("replace_doc.txt", "r", encoding='utf-8') as file:
        replace_txt = file.readlines()
    for str in replace_txt:
        replace_str.append(str.rstrip().split(';'))
    return replace_str



def main():
    for file in get_files():
        replace_doc(file)

if __name__ == '__main__':
    main()