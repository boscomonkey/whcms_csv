from random import choice

# removed ambiguous characters: i, l, o, 1, 0
# removed ambiguous symbol: |, \, ;
# removed comma as it screws with CSV
charsets = [
    "abcdefghjkmnpqrstuvwxyz",
    "ABCDEFGHJKMNPQRSTUVWXYZ",
    "23456789",
    "^$%&/()=?{[]}+~#-_.:;<>",
]


def make_password(length=12):
    all_chars = "".join(charsets)
    pwd = []
    while len(pwd) < length:
        rand_char = choice(all_chars)
        if rand_char not in pwd:
            pwd.append(rand_char)
    return "".join(pwd)
