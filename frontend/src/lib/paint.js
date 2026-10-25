// rough paint shades for the color names people usually type in
const PAINT = {
  black: "#1c1d20",
  white: "#f4f4f2",
  silver: "#b9bec6",
  grey: "#7d838c",
  gray: "#7d838c",
  red: "#b5302a",
  blue: "#2a5db0",
  green: "#3f6b47",
  teal: "#22808a",
  yellow: "#e8b923",
  orange: "#d96b27",
  bronze: "#8c6239",
  brown: "#6b4a33",
  maroon: "#6d1f2a",
  beige: "#cdbb98",
  gold: "#c9a43b",
  purple: "#5b3c88",
};

export function paintFor(colorName) {
  if (!colorName) return "#9aa0a8";
  const key = colorName.trim().toLowerCase().split(/\s+/).pop();
  return PAINT[key] || "#9aa0a8";
}
