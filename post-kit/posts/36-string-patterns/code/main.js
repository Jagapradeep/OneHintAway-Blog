function isPalindrome(word) {
    let left = 0;
    let right = word.length - 1;
    while (left < right) {
        if (word[left] !== word[right]) {
            return false;
        }
        left++;
        right--;
    }
    return true;
}

function isAnagram(s, t) {
    const counts = new Array(26).fill(0);
    for (const letter of s) {
        const k = letter.charCodeAt(0) - 97; // alphabet index
        counts[k] = counts[k] + 1;
    }
    for (const letter of t) {
        const k = letter.charCodeAt(0) - 97;
        counts[k] = counts[k] - 1;
    }
    for (const count of counts) {
        if (count !== 0) {
            return false;
        }
    }
    return true;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [s, t] = l.split("|"); return isAnagram(s, t) + " " + isPalindrome(s); }).join("\n"));
