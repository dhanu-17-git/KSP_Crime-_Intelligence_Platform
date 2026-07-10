import re

def phonetic_hash(name: str | None) -> str:
    """Generate a phonetic hash key for a name to resolve spelling/transliteration variations.
    
    This is a simplified Metaphone-like algorithm adapted for Indian names:
    - Normalizes common vowels, double letters, and silent characters.
    - Maps similar sound groups (e.g. V/W, B/P, G/K, J/Z).
    - Drops silent letters.
    """
    if not name:
        return ""
    
    # 1. Lowercase and strip non-alpha characters
    s = name.lower()
    s = re.sub(r"[^a-z]", "", s)
    if not s:
        return ""
        
    # 2. Normalize common transliterated clusters
    s = re.sub(r"sh", "s", s)
    s = re.sub(r"ch", "s", s)
    s = re.sub(r"th", "t", s)
    s = re.sub(r"dh", "t", s)
    s = re.sub(r"gh", "k", s)
    s = re.sub(r"bh", "p", s)
    s = re.sub(r"ph", "f", s)
    s = re.sub(r"jh", "j", s)
    s = re.sub(r"kh", "k", s)
    
    # 3. Collapse double letters
    s = re.sub(r"([a-z])\1+", r"\1", s)
    
    # 4. Map spelling variations common in South Indian names (e.g. Gowda/Gouda, Sunil/Suneel)
    s = re.sub(r"ow", "u", s)
    s = re.sub(r"ou", "u", s)
    s = re.sub(r"ee", "i", s)
    s = re.sub(r"oo", "u", s)
    s = re.sub(r"y", "i", s)
    s = re.sub(r"w", "v", s)
    
    # 5. Drop vowels unless they start the name
    first_char = s[0]
    rest = s[1:]
    rest = re.sub(r"[aeiou]", "", rest)
    s = first_char + rest
    
    # 6. Translate to phonetic groups
    # B,P,F -> P
    # C,G,J,K,Q,S,X,Z -> S
    # D,T -> T
    # L -> L
    # M,N -> M
    # R -> R
    # V -> V
    translated = []
    for c in s:
        if c in "bpf":
            translated.append("p")
        elif c in "cgjkqsxz":
            translated.append("s")
        elif c in "dt":
            translated.append("t")
        elif c in "l":
            translated.append("l")
        elif c in "mn":
            translated.append("m")
        elif c in "r":
            translated.append("r")
        elif c in "v":
            translated.append("v")
        else:
            translated.append(c) # keep first vowel if it remained
            
    res = "".join(translated)
    return res[:6].upper()
