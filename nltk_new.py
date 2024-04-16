import os
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, RegexpParser
import xml.etree.ElementTree as ET

# Function to parse XML files and extract sentences
def parse_xml(xml_folder):
    sentences = []
    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            tree = ET.parse(os.path.join(xml_folder, filename))
            root = tree.getroot()
            for dataitem in root.findall('dataitem'):
                sentence = dataitem.find('sentence').text.strip()
                sentences.append(sentence)
    return sentences

# Function to identify action items
def identify_action_items(sentences):
    action_items = []
    grammar = r"""
        NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
        PP: {<IN><NP>}               # chunk prepositions followed by NP
        VP: {<VB.*><NP|PP|CLAUSE>+$} # chunk verbs and their arguments
        CLAUSE: {<NP><VP>}           # chunk NP, VP
    """
    chunk_parser = RegexpParser(grammar)
    
    for sentence in sentences:
        tagged_sentence = pos_tag(word_tokenize(sentence))
        parsed_sentence = chunk_parser.parse(tagged_sentence)
        for subtree in parsed_sentence.subtrees():
            if subtree.label() == 'VP':
                action_items.append(' '.join(word for word, tag in subtree.leaves()))
    
    return action_items

# Main function
def main():
    # Paths to training and testing folders
    training_folder = 'path_to_training_folder'
    testing_folder = 'path_to_testing_folder'

    # Parse XML files
    training_sentences = parse_xml(training_folder)
    testing_sentences = parse_xml(testing_folder)

    # Identify action items
    training_action_items = identify_action_items(training_sentences)
    testing_action_items = identify_action_items(testing_sentences)

    # Print identified action items
    print("Training Action Items:")
    for action_item in training_action_items:
        print(action_item)
    
    print("\nTesting Action Items:")
    for action_item in testing_action_items:
        print(action_item)

if __name__ == "__main__":
    main()
