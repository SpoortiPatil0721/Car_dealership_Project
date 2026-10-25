import { paintFor } from "../lib/paint.js";

// hand drawn side profiles, one per body style
const BODIES = {
  sedan: {
    body: "M18 78 L18 66 Q20 58 34 56 L70 52 L92 36 Q98 32 110 32 L150 32 Q160 32 168 38 L186 52 L214 56 Q224 58 224 66 L224 78 Z",
    glass: "M98 38 L150 38 L172 52 L86 52 Z",
    pillar: 128,
  },
  suv: {
    body: "M16 80 L16 58 Q18 50 30 48 L62 46 L78 24 Q82 20 92 20 L196 20 Q206 20 210 28 L222 48 Q226 52 226 60 L226 80 Z",
    glass: "M84 28 L200 28 L212 46 L72 46 Z",
    pillar: 140,
  },
  hatchback: {
    body: "M24 80 L24 64 Q26 56 38 54 L72 50 L96 30 Q100 27 110 27 L176 27 Q186 27 192 38 L204 62 L206 80 Z",
    glass: "M102 34 L176 34 L188 50 L84 50 Z",
    pillar: 138,
  },
  coupe: {
    body: "M14 80 L14 68 Q16 60 30 58 L84 54 L112 36 Q118 33 128 33 L156 33 Q172 33 190 46 L216 58 Q226 62 226 70 L226 80 Z",
    glass: "M118 40 L156 40 Q168 40 182 52 L100 52 Z",
    pillar: null,
  },
  pickup: {
    body: "M14 80 L14 60 Q16 52 28 50 L62 48 L76 26 Q80 22 90 22 L128 22 Q134 22 134 30 L134 50 L226 50 L226 80 Z",
    glass: "M84 30 L126 30 L126 48 L70 48 Z",
    pillar: null,
  },
};

function bodyFor(category = "") {
  const name = category.toLowerCase();
  if (name.includes("suv") || name.includes("van") || name.includes("crossover")) return BODIES.suv;
  if (name.includes("hatch")) return BODIES.hatchback;
  if (name.includes("coupe") || name.includes("sport") || name.includes("convertible")) return BODIES.coupe;
  if (name.includes("pickup") || name.includes("truck")) return BODIES.pickup;
  return BODIES.sedan;
}

export default function CarArt({ category, color, soldOut = false, className = "" }) {
  const shape = bodyFor(category);
  const isElectric = (category || "").toLowerCase().includes("electric");

  return (
    <svg viewBox="0 0 240 104" className={className} role="img" aria-label={`${color || ""} ${category || "car"}`.trim()}>
      <ellipse cx="120" cy="94" rx="104" ry="5" fill="#000" opacity="0.18" />
      <g opacity={soldOut ? 0.45 : 1}>
        <path d={shape.body} fill={paintFor(color)} stroke="#1c1d20" strokeWidth="2" strokeLinejoin="round" />
        <path d={shape.glass} fill="#cfe0ee" stroke="#1c1d20" strokeWidth="1.5" strokeLinejoin="round" />
        {shape.pillar && <line x1={shape.pillar} y1="26" x2={shape.pillar} y2="54" stroke="#1c1d20" strokeWidth="3" />}
        <rect x="20" y="64" width="10" height="5" rx="1.5" fill="#fff4c2" />
        <rect x="214" y="64" width="8" height="5" rx="1.5" fill="#d9483b" />
        {[62, 180].map((x) => (
          <g key={x}>
            <circle cx={x} cy="80" r="15" fill="#1c1d20" />
            <circle cx={x} cy="80" r="7" fill="#b9bec6" />
          </g>
        ))}
        {isElectric && <path d="M118 58 L110 70 L118 70 L114 80 L126 66 L118 66 Z" fill="#f2c230" stroke="#1c1d20" strokeWidth="1" />}
      </g>
    </svg>
  );
}
