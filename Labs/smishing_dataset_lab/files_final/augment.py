import random
import pandas as pd
from nltk.corpus import wordnet

from Labs.smishing_dataset_lab.smishingDB import SmishingDB
from Backend.Analysis.regexStripper import regexStripper as res

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

def synonym_replacement(sentence, n):
    # strip links from sentence:
    sentence_without_urls, urls = res.link_stripper(sentence)
    words = sentence_without_urls.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(synonyms)
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n: 
            break

    sentence = ' '.join(new_words)
    #add back the urls to the end of the sentence:
    sentence = add_urls_back(sentence, urls)
    return sentence

def augment_texts(text, num_augmentations=5):
    text_without_urls, urls = res.link_stripper(text)
    augmented_texts = [add_urls_back(synonym_replacement(text_without_urls, random.randint(1, 3)), urls) for _ in range(num_augmentations)]
    return augmented_texts

def augment_messages_by_label(db, label, num_augmentations=5):
    data = db.get_data_object()
    labeled_data = data[data['LABEL'] == label]
    augmented_data = []
    
    for index, row in labeled_data.iterrows():
        augmented_texts = augment_texts(row['TEXT'], num_augmentations)
        for text in augmented_texts:
            augmented_data.append({'LABEL': row['LABEL'], 'TEXT': text})
    
    augmented_df = pd.DataFrame(augmented_data)
    return augmented_df

def add_urls_back(text, urls):
    for url in urls:
        text += " " + url
    return text

def main():
    # Initialize the database
    db = SmishingDB('Labs/smishing_dataset_lab/files_final/smishing_messages.csv')
    db.open_file()
    
    # Augment the messages labeled as 'Smishing'
    augmented_data1 = augment_messages_by_label(db, 0, num_augmentations=5)
    augmented_data2 = augment_messages_by_label(db, 1, num_augmentations=5)

    # Inflate the original data with the augmented data
    db.inflate_data_with_dataframe(pd.concat([augmented_data1, augmented_data2]))
    
    # Save the augmented data to a new CSV file
    db.save_data_to_file('Labs/smishing_dataset_lab/files_final/smishing_messages_augmented.csv')

if __name__ == "__main__":
    main()