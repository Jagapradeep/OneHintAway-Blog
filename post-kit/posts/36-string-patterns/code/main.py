def is_palindrome(word):
    left = 0
    right = len(word) - 1
    while left < right:
        if word[left] != word[right]:
            return False
        left += 1
        right -= 1
    return True


def is_anagram(s, t):
    counts = [0] * 26
    for letter in s:
        k = ord(letter) - ord("a")  # alphabet index
        counts[k] = counts[k] + 1
    for letter in t:
        k = ord(letter) - ord("a")
        counts[k] = counts[k] - 1
    for count in counts:
        if count != 0:
            return False
    return True
# ---- test harness: not on the blog ----
import sys
tf = lambda x: "true" if x else "false"
for line in sys.stdin.read().split("\n")[:-1]:
    s, t = line.split("|")
    print(tf(is_anagram(s, t)), tf(is_palindrome(s)))
