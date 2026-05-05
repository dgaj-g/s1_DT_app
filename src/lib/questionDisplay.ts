const publicHelperSuffixPattern = /(?:^|\s+)Pairs:\s.*$/is;
const publicArrowHelperPattern = /(?:^|\s)[^.\n]+→\s*\?(?:\s*;[^.\n]+→\s*\?)+/is;

export function cleanQuestionStemForDisplay(value: unknown) {
  return String(value || "")
    .replace(publicHelperSuffixPattern, "")
    .replace(publicArrowHelperPattern, "")
    .trim();
}

export function isPublicHelperText(value: unknown) {
  const text = String(value || "").trim();
  return publicHelperSuffixPattern.test(text) || publicArrowHelperPattern.test(text);
}
