# Gallery Layout Library Plan

## Overview
Create a standalone JavaScript library that provides multiple layout algorithms for image galleries, with a clean API and minimal dependencies.

---

## 1. Architecture

### Core Components

```
gallery-layouts/
├── src/
│   ├── index.js              # Main entry point, exports public API
│   ├── GalleryLayout.js      # Base class / core controller
│   ├── layouts/
│   │   ├── MasonryLayout.js    # Wraps Masonry.js
│   │   ├── JustifiedLayout.js  # Uses justified-layout algorithm
│   │   ├── SquareLayout.js     # Pure CSS Grid
│   │   ├── OverflowHeightLayout.js  # Single column, full width
│   │   └── FitScreenLayout.js  # Single column, viewport-constrained
│   ├── utils/
│   │   ├── dom.js            # DOM manipulation helpers
│   │   └── images.js         # Image loading utilities
│   └── styles/
│       └── gallery.css       # Base styles (optional, can be injected)
├── dist/                     # Built files
├── examples/
├── package.json
└── README.md
```

---

## 2. API Design

### Initialization
```javascript
import { Gallery } from 'gallery-layouts';

const gallery = new Gallery('#container', {
  images: ['img1.jpg', 'img2.jpg', ...],
  layout: 'masonry',  // 'masonry' | 'justified' | 'square' | 'overflow-height' | 'fit-screen'
  gutter: 15,
  maxWidth: 1400,
});
```

### Methods
```javascript
gallery.setLayout('justified');      // Switch layout
gallery.setImages([...]);            // Update images
gallery.addImages([...]);            // Append images
gallery.refresh();                   // Re-render current layout
gallery.destroy();                   // Cleanup
```

### Events
```javascript
gallery.on('layoutChange', (layoutName) => {});
gallery.on('imagesLoaded', () => {});
gallery.on('imageClick', (src, index) => {});
```

### Layout-Specific Options
```javascript
const gallery = new Gallery('#container', {
  layout: 'justified',
  layoutOptions: {
    justified: { rowHeight: 200, maxRowHeight: 300 },
    masonry: { columns: 4 },
    square: { columns: 4 },
    fitScreen: { padding: 30 },
  }
});
```

---

## 3. Implementation Phases

### Phase 1: Core Structure
1. **Create base `GalleryLayout` class** with common interface:
   - `render(items, container)`
   - `destroy()`
   - `refresh()`
   
2. **Extract each layout into separate classes** implementing the interface

3. **Create main `Gallery` controller** that:
   - Manages container element
   - Holds current layout instance
   - Handles switching between layouts
   - Manages item state

### Phase 2: Reduce Dependencies

| Current | Target |
|---------|--------|
| Masonry.js | Keep (or implement simple version) |
| jQuery | Remove - use vanilla JS |
| Justified Gallery | Replace with `justified-layout` (algorithm only, ~3KB) |
| imagesLoaded | Keep (small, useful) |

4. **Remove jQuery dependency** - rewrite Justified layout using vanilla JS + `justified-layout` npm package

5. **Make Masonry.js optional** - provide fallback CSS-only masonry using `column-count` for simpler cases

### Phase 3: Build & Package
6. **Set up build tooling**:
   - Rollup or esbuild for bundling
   - Output: ESM, CJS, UMD formats
   - TypeScript definitions

7. **CSS handling options**:
   - Inject styles automatically
   - Export CSS file for manual inclusion
   - CSS-in-JS option

### Phase 4: Enhancements
8. **Add features**:
   - Lazy loading support
   - Responsive breakpoints config
   - Animation options (opt-in)
   - Virtual scrolling for large galleries
   - Placeholder/skeleton loading

9. **Framework wrappers** (optional):
   - React: `<Gallery layout="masonry" images={[...]} />`
   - Vue: `<Gallery :layout="masonry" :images="[...]" />`

---

## 4. Key Decisions

| Decision | Recommendation |
|----------|----------------|
| **Dependency strategy** | Peer dependencies for Masonry, bundle justified-layout |
| **Styling** | Ship CSS file + option to inject, use CSS custom properties for theming |
| **Item data format** | Support both string array and object array (see below) |
| **Responsive** | Use ResizeObserver, configurable breakpoints |
| **Bundle size target** | < 10KB gzipped (excluding optional Masonry) |

---

## 5. Item Data Format

Support flexible input formats:

```javascript
// Simple: array of image URLs
const images = ['photo1.jpg', 'photo2.jpg'];

// Rich: array of item objects
const items = [
  { 
    type: 'image',           // 'image' | 'text' (future)
    src: 'photo1.jpg', 
    alt: 'Description',
    width: 1200,             // Optional: known dimensions for faster layout
    height: 800,
    caption: 'Photo caption' // Future: caption support
  },
  {
    type: 'text',            // Future: text block support
    content: 'Long form text content...',
    aspectRatio: 1.5         // Treat as box with this aspect ratio
  }
];
```

---

## 6. Example Usage (Final API)

```javascript
// Minimal
const gallery = new Gallery('#photos', {
  images: photoUrls,
  layout: 'masonry'
});

// Full options
const gallery = new Gallery('#photos', {
  items: photos.map(p => ({ 
    type: 'image',
    src: p.url, 
    alt: p.title, 
    width: p.w, 
    height: p.h,
    caption: p.caption
  })),
  layout: 'justified',
  gutter: 15,
  maxWidth: 1400,
  responsive: {
    1200: { columns: 4 },
    768: { columns: 3 },
    480: { columns: 2 },
    0: { columns: 1 }
  },
  layoutOptions: {
    justified: { rowHeight: 200 }
  },
  onItemClick: (item, index) => openLightbox(item.src)
});

// Switch layout
document.querySelector('#layoutSelect').addEventListener('change', (e) => {
  gallery.setLayout(e.target.value);
});
```

---

## 7. Future Features

### Captions on Images
- Optional caption text displayed below or overlaid on images
- Configurable position: `'below'` | `'overlay'` | `'hover'`
- Caption affects layout height calculations in some layouts

```javascript
{
  type: 'image',
  src: 'photo.jpg',
  caption: 'A beautiful sunset over the mountains',
  captionPosition: 'below'  // or 'overlay', 'hover'
}
```

### Text Blocks as Layout Elements
- Treat text content as a layout element alongside images
- Specify aspect ratio or fixed dimensions
- Useful for:
  - Story-style galleries mixing photos and narrative
  - Pull quotes or section headers
  - Metadata or date separators

```javascript
{
  type: 'text',
  content: 'Summer 2025 - Our trip to Iceland...',
  aspectRatio: 1.2,         // Width/height ratio for layout
  // OR
  width: 400,
  height: 300,
  style: 'quote'            // Optional styling hint: 'quote' | 'header' | 'body'
}
```

### Layout Considerations for Mixed Content
- Justified: Text blocks participate in row balancing
- Masonry: Text blocks flow like images with calculated heights
- Square: Text blocks get cropped/scrollable or excluded
- Fit-screen: Text blocks centered, sized to fit viewport

---

## 8. Next Steps

- [ ] Phase 1: Extract current code into class-based structure
- [ ] Phase 1: Define TypeScript interfaces for items and options
- [ ] Phase 2: Replace jQuery + Justified Gallery with vanilla JS + justified-layout
- [ ] Phase 2: Write tests for each layout
- [ ] Phase 3: Set up npm package with build tooling
- [ ] Phase 4: Add caption support
- [ ] Phase 4: Add text block support
- [ ] Phase 4: Framework wrappers (React, Vue)

---

## Appendix: Dependency Comparison

### justified-layout vs Justified Gallery

| Aspect | justified-layout (Flickr) | Justified Gallery |
|--------|---------------------------|-------------------|
| **What it does** | Algorithm only - returns coordinates | Full plugin - handles everything |
| **Dependencies** | None | jQuery (~30KB) |
| **Size** | ~3KB gzipped | ~15KB + jQuery |
| **Flexibility** | High - you control rendering | Low - opinionated |
| **Framework support** | Any | jQuery only |

**Recommendation**: Use `justified-layout` for a modern, lightweight library.
