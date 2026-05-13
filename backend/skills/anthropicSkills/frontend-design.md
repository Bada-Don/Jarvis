---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

# Frontend Design Skill

## Design Thinking

Before coding, understand the context and commit to a **BOLD aesthetic direction:**

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc.
- **Constraints**: Technical requirements (framework, performance, accessibility)
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

## Aesthetics Guidelines

### Typography
- Choose fonts that are beautiful, unique, and interesting
- Avoid generic fonts like Arial and Inter
- Pair a distinctive display font with a refined body font
- Unexpected, characterful font choices elevate the entire design

### Color & Theme
- Commit to a cohesive aesthetic
- Use CSS variables for consistency
- Dominant colors with sharp accents outperform timid, evenly-distributed palettes
- Design for the specific context, not generic defaults

### Motion
- Use animations for effects and micro-interactions
- Prioritize CSS-only solutions for HTML
- Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions
- Use scroll-triggering and hover states that surprise

### Spatial Composition
- Unexpected layouts
- Asymmetry, overlap, diagonal flow
- Grid-breaking elements
- Generous negative space OR controlled density

### Backgrounds & Visual Details
- Create atmosphere and depth rather than defaulting to solid colors
- Add contextual effects and textures matching the overall aesthetic
- Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays

## What NOT to Do

NEVER use generic AI-generated aesthetics like:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Cliched color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

**Interpret creatively and make unexpected choices** that feel genuinely designed for the context. No design should be the same.

## Implementation Complexity

Match implementation complexity to the aesthetic vision:
- **Maximalist designs** need elaborate code with extensive animations and effects
- **Minimalist or refined designs** need restraint, precision, and careful attention to spacing, typography, and subtle details
- Elegance comes from executing the vision well

## Technical Stack

### HTML/CSS/JS
- Use CSS variables for theming and consistency
- CSS Grid and Flexbox for sophisticated layouts
- CSS animations for motion (preferred over JS for performance)
- Keep JS minimal unless interactivity demands it

### React
- Functional components with hooks
- Use Tailwind core utility classes only (no compiler, so only pre-defined base-stylesheet classes work)
- Available libraries: lucide-react, recharts, mathjs, lodash, d3, plotly, three, papaparse, SheetJS, shadcn/ui, chart.js, tone, mammoth, tensorflow
- No localStorage or sessionStorage — use React state (useState, useReducer)

### Design Tokens
- Load `read_me` module before generating output to get current CSS vars, colors, dimensions, fonts, and technical constraints
- The module is authoritative for design specifics in your target environment

## Process

1. **Read the context** — what's the problem, audience, constraints?
2. **Choose a bold aesthetic** — commit to it fully
3. **Plan the layout** — sketch spatial relationships, not wireframes
4. **Implement with code** — HTML/CSS/JS or React
5. **Iterate on refinement** — polish motion, spacing, typography
6. **Review** — does the design match the aesthetic vision? Is every detail intentional?

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
