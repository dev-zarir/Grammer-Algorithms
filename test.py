import string
from PyDictionary import PyDictionary

masculine_words = ["Male", "Man", "Gentleman", "Boy", "Bachelor", "He", "His", "Him", "Mr", "Sir", "Father", "Son", "Brother", "Uncle", "Husband", "Boyfriend", "Masculine", "Manly", "Men"]

feminine_words = ["Woman","Girl","Lady","Female","Dame","Miss","Madam","Queen","Goddess","She","Her","Hers","Feminine","Womanly","Female-identifying","Female-presenting","Matron","Duchess","Princess","Mademoiselle"]

common_words = ["Individual", "Being", "Entities", "Creature", "Mortal", "Soul", "Entities", "Personage", "Humanoid", "Lifeform", "Person", "Progeny", "Offspring", "Descendant", "Ancestor", "Family member", "Kin", "Relative", "Companion", "Peer"]

info=PyDictionary()

translator = str.maketrans('', '', string.punctuation)

def get_definition_word_list(word:str):
    info_dict=info.meaning(word)
    wl=[]
    if info_dict:
        for key, value in info_dict.items():
            for val in value:
                for i in val.split(" "):
                    wl.append(i.lower().translate(translator))
        new_wl=list(set(wl))
        new_wl.sort()
        return new_wl
    else: return []

print(get_definition_word_list("zero"))
print(info.meaning("zero"))