import sys
new_words = ['dog','cat','bird']

# spanish.txt should be a utf-8 text file where odd line is english word
# and even is spanish word. should end evenly
f = open('spanish.txt', 'r')

# the words are decoded and appended to a list
english_spanish_words = []
for line in f:
    dec = line.decode("utf-8")
    enc = dec.encode("utf-8")
    stripped = enc.replace("\n", "")
    english_spanish_words.append(stripped)

# english spanish words are paired into tuples 
# pairs = zip(english_spanish_words[0::2], english_spanish_words[1::2])

# push words to datastore. even lines are spanish translations
#for i in english_spanish_words:
#    print i

