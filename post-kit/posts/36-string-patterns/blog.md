Asked whether two words use the same letters, or whether a word reads the same both ways? Two small string moves cover both. Worked examples: **stone** and **notes**, and **racecar**.

## The idea

**The frequency array.** Picture two bags of letter tiles. Tally the first bag up on a board with one box per letter, then tally the second bag down. If every box ends at 0, the bags hold the same tiles, and no sorting is needed.

In code the board is an array of 26 counts. Letter a goes in box 0, b in box 1, and so on to z in box 25; the box number is the letter's alphabet index (s is {{INDEX_S}}). Count every letter of `s` up and every letter of `t` down, then check all 26 boxes. This is LeetCode 242, Valid Anagram, for lowercase letters.

**The palindrome check.** A palindrome reads the same both ways. Put `left` on the first letter and `right` on the last. If they differ, it isn't a palindrome; if they match, step both inwards. When they meet, every pair has matched.

## The walk

Counting stone up, then notes down, in the boxes for e, n, o, s and t:

| Step | e | n | o | s | t |
| --- | --- | --- | --- | --- | --- |
| start | 0 | 0 | 0 | 0 | 0 |
| after stone | 1 | 1 | 1 | 1 | 1 |
| after notes | 0 | 0 | 0 | 0 | 0 |

Every box is back at 0, so notes is an anagram of stone. For racecar, the pairs r and r, a and a, c and c match, and the pointers meet at e: a palindrome.

Quick check: counting below up and elbow down leaves **{{nonzero('below', 'elbow')}}** boxes that are not 0, so they are anagrams.

## Pseudocode

`isPalindrome` walks two pointers inwards; `isAnagram` counts one word up and the other down.

{{PSEUDOCODE}}

**The trap:** skip the final loop over the counts and return true. For stone and note, the s box is still 1, but the check never looks: it answers {{tf(wrong_anagram('stone', 'note'))}} instead of {{tf(is_anagram('stone', 'note'))}}. Counting `t` down only catches letters `t` has too many of; the final check catches letters it is missing.

{{CODE}}

The code assumes lowercase letters a to z, as LeetCode 242 does. For other characters, use a hash map from [post 05](/posts/hashing/) instead of the 26 boxes.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Anagram check | O(n) time, O(1) space | One pass over each word; always 26 counts |
| Palindrome check | O(n) time, O(1) space | Each pair is compared once |
| Sort both words | O(n log n) | The slower way to compare letters |

## How it was tested

{{TESTED}}
