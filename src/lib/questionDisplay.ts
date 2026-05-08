const publicHelperSuffixPattern = /(?:^|\s+)Pairs:\s.*$/is;
const publicArrowHelperPattern = /(?:^|\s)[^.\n]+→\s*\?(?:\s*;[^.\n]+→\s*\?)+/is;
const publicTermsSuffixPattern = /(?:^|\s+)Terms:\s.*$/is;

export function cleanQuestionStemForDisplay(value: unknown) {
  return String(value || "")
    .replace(publicHelperSuffixPattern, "")
    .replace(publicTermsSuffixPattern, "")
    .replace(publicArrowHelperPattern, "")
    .trim();
}

export function isPublicHelperText(value: unknown) {
  const text = String(value || "").trim();
  return (
    publicHelperSuffixPattern.test(text) ||
    publicTermsSuffixPattern.test(text) ||
    publicArrowHelperPattern.test(text)
  );
}
