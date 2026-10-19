// Deterministic 8-slot category color hashing according to DesignDoc.md Section 3.4

export function getCategorySlot(categoryName) {
  if (!categoryName || typeof categoryName !== 'string') return 1;
  let hash = 0;
  for (let i = 0; i < categoryName.length; i++) {
    hash = (hash << 5) - hash + categoryName.charCodeAt(i);
    hash |= 0;
  }
  return (Math.abs(hash) % 8) + 1;
}

export function getCategoryClass(categoryName) {
  return `category-slot-${getCategorySlot(categoryName)}`;
}
