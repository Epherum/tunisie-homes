# Mapbox Integration Guide

Quick reference for integrating Mapbox GL JS with your geocoded property data.

---

## Prerequisites

✅ Properties have `latitude` and `longitude` fields (via Nominatim)
✅ PostGIS enabled in Supabase
✅ Mapbox account (free tier is sufficient)

---

## Setup

### 1. Install Mapbox

```bash
cd frontend
npm install mapbox-gl react-map-gl
```

### 2. Get Mapbox Token

1. Go to [mapbox.com](https://account.mapbox.com/)
2. Create account (free)
3. Get your **public token** from dashboard

### 3. Add to Environment Variables

```env
# frontend/.env
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

---

## Basic Map Component

### Simple Property Map

```typescript
// components/PropertyMap.tsx
'use client';

import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Property {
  id: string;
  title: string;
  price: number;
  latitude: number;
  longitude: number;
}

export default function PropertyMap({ properties }: { properties: Property[] }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

    // Initialize map centered on Tunisia
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // Dark mode (PRD requirement)
      center: [9.5, 34.0], // Tunisia center
      zoom: 6
    });

    // Add markers for each property
    properties.forEach(property => {
      if (property.latitude && property.longitude) {
        const marker = new mapboxgl.Marker({ color: '#3B82F6' })
          .setLngLat([property.longitude, property.latitude])
          .setPopup(
            new mapboxgl.Popup().setHTML(`
              <h3 class="font-bold">${property.title}</h3>
              <p class="text-sm">${property.price.toLocaleString()} TND</p>
            `)
          )
          .addTo(map.current!);
      }
    });

    return () => {
      map.current?.remove();
    };
  }, [properties]);

  return <div ref={mapContainer} className="w-full h-full" />;
}
```

---

## Advanced: Clustered Map

For 100+ properties, use clustering to avoid marker overlap.

```typescript
// components/ClusteredPropertyMap.tsx
'use client';

import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';

export default function ClusteredPropertyMap({ properties }) {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN!;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [9.5, 34.0],
      zoom: 6
    });

    map.current.on('load', () => {
      // Convert properties to GeoJSON
      const geojson = {
        type: 'FeatureCollection',
        features: properties.map(prop => ({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [prop.longitude, prop.latitude]
          },
          properties: {
            id: prop.id,
            title: prop.title,
            price: prop.price,
            propertyType: prop.propertyType,
            dealRating: prop.dealRating
          }
        }))
      };

      // Add source
      map.current.addSource('properties', {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 50
      });

      // Cluster circles
      map.current.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'properties',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': [
            'step',
            ['get', 'point_count'],
            '#3B82F6', 10,
            '#10B981', 30,
            '#F59E0B'
          ],
          'circle-radius': [
            'step',
            ['get', 'point_count'],
            20, 10,
            30, 30,
            40
          ]
        }
      });

      // Cluster count
      map.current.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'properties',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
          'text-size': 12
        },
        paint: {
          'text-color': '#ffffff'
        }
      });

      // Unclustered points
      map.current.addLayer({
        id: 'unclustered-point',
        type: 'circle',
        source: 'properties',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': '#3B82F6',
          'circle-radius': 8,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff'
        }
      });

      // Click handler
      map.current.on('click', 'unclustered-point', (e) => {
        const coordinates = e.features[0].geometry.coordinates.slice();
        const { title, price } = e.features[0].properties;

        new mapboxgl.Popup()
          .setLngLat(coordinates)
          .setHTML(`
            <div class="p-2">
              <h3 class="font-bold text-sm">${title}</h3>
              <p class="text-xs">${price.toLocaleString()} TND</p>
            </div>
          `)
          .addTo(map.current);
      });

      // Cursor pointer on hover
      map.current.on('mouseenter', 'unclustered-point', () => {
        map.current.getCanvas().style.cursor = 'pointer';
      });
      map.current.on('mouseleave', 'unclustered-point', () => {
        map.current.getCanvas().style.cursor = '';
      });
    });

    return () => map.current?.remove();
  }, [properties]);

  return <div ref={mapContainer} className="w-full h-full" />;
}
```

---

## Heatmap Mode (PRD FR-09)

```typescript
// Add heatmap layer
map.current.addLayer({
  id: 'price-heatmap',
  type: 'heatmap',
  source: 'properties',
  paint: {
    // Increase weight as price increases
    'heatmap-weight': [
      'interpolate',
      ['linear'],
      ['get', 'price'],
      0, 0,
      1000000, 1
    ],
    // Increase intensity as zoom increases
    'heatmap-intensity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      0, 1,
      9, 3
    ],
    // Color ramp for heatmap (blue = cheap, red = expensive)
    'heatmap-color': [
      'interpolate',
      ['linear'],
      ['heatmap-density'],
      0, 'rgba(33,102,172,0)',
      0.2, 'rgb(103,169,207)',
      0.4, 'rgb(209,229,240)',
      0.6, 'rgb(253,219,199)',
      0.8, 'rgb(239,138,98)',
      1, 'rgb(178,24,43)'
    ],
    'heatmap-radius': 30,
    'heatmap-opacity': 0.7
  }
}, 'waterway-label');

// Toggle heatmap
function toggleHeatmap() {
  const visibility = map.current.getLayoutProperty('price-heatmap', 'visibility');
  if (visibility === 'visible') {
    map.current.setLayoutProperty('price-heatmap', 'visibility', 'none');
  } else {
    map.current.setLayoutProperty('price-heatmap', 'visibility', 'visible');
  }
}
```

---

## 3D Extrusion (PRD Visualization)

Show expensive neighborhoods as taller buildings.

```typescript
// After loading neighborhood polygons
map.current.addLayer({
  id: '3d-neighborhoods',
  type: 'fill-extrusion',
  source: 'neighborhoods',
  paint: {
    // Extrude based on average price
    'fill-extrusion-height': [
      '*',
      ['get', 'avgPrice'],
      0.01 // Scale factor
    ],
    'fill-extrusion-base': 0,
    // Color by price (green = cheap, red = expensive)
    'fill-extrusion-color': [
      'interpolate',
      ['linear'],
      ['get', 'avgPrice'],
      100000, '#10B981',
      500000, '#F59E0B',
      1000000, '#EF4444'
    ],
    'fill-extrusion-opacity': 0.8
  }
});
```

---

## Deal Rating Colors (PRD FR-05)

Color markers by deal rating (green = good deal, red = overpriced).

```typescript
// In paint property
paint: {
  'circle-color': [
    'interpolate',
    ['linear'],
    ['get', 'dealRating'],
    0, '#EF4444',   // Red (bad deal)
    50, '#F59E0B',  // Orange (fair)
    80, '#10B981'   // Green (good deal)
  ],
  'circle-radius': 10
}
```

---

## Server Component Example

Fetch properties server-side for better performance.

```typescript
// app/map/page.tsx
import { prisma } from '@/lib/prisma';
import PropertyMap from '@/components/PropertyMap';

export default async function MapPage() {
  // Fetch properties with coordinates
  const properties = await prisma.property.findMany({
    where: {
      latitude: { not: null },
      longitude: { not: null },
      status: 'ACTIVE'
    },
    select: {
      id: true,
      title: true,
      price: true,
      latitude: true,
      longitude: true,
      propertyType: true,
      dealRating: true,
      images: {
        take: 1,
        orderBy: { order: 'asc' }
      }
    },
    take: 100 // Limit for performance
  });

  return (
    <div className="h-screen w-full">
      <PropertyMap properties={properties} />
    </div>
  );
}
```

---

## Spatial Queries with PostGIS

For "properties near me" or distance-based searches.

```typescript
// Find properties within 5km of a point
const nearbyProperties = await prisma.$queryRaw`
  SELECT *
  FROM properties
  WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography,
    5000  -- 5km in meters
  )
  ORDER BY
    ST_Distance(
      location,
      ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography
    )
  LIMIT 20;
`;
```

---

## Custom Marker Icons (Deal Rating)

```typescript
// Create custom marker based on deal rating
function createMarker(property: Property) {
  const el = document.createElement('div');
  el.className = 'custom-marker';

  // Color based on deal rating
  const color = property.dealRating > 70 ? '#10B981' :
                property.dealRating > 50 ? '#F59E0B' : '#EF4444';

  el.style.backgroundColor = color;
  el.style.width = '30px';
  el.style.height = '30px';
  el.style.borderRadius = '50%';
  el.style.border = '2px solid white';
  el.style.display = 'flex';
  el.style.alignItems = 'center';
  el.style.justifyContent = 'center';
  el.style.fontWeight = 'bold';
  el.style.color = 'white';
  el.style.fontSize = '12px';
  el.textContent = `${property.dealRating}`;

  return new mapboxgl.Marker(el)
    .setLngLat([property.longitude, property.latitude])
    .addTo(map);
}
```

---

## Performance Tips

1. **Limit Results**: Only load visible properties
   ```typescript
   // Only fetch properties in viewport
   const bounds = map.current.getBounds();
   const properties = await fetchPropertiesInBounds(bounds);
   ```

2. **Use GeoJSON Source**: Faster rendering for 100+ markers
3. **Enable Clustering**: Above 50 properties
4. **Lazy Load Images**: Don't load property images until popup opens
5. **Debounce Updates**: Wait for user to stop panning before refetching

---

## Dark Mode (PRD Requirement)

```typescript
// Use dark Mapbox style
style: 'mapbox://styles/mapbox/dark-v11'

// Or create custom style at mapbox.com/studio
style: 'mapbox://styles/your-username/your-style-id'
```

---

## Split Screen Layout (PRD FR-08)

```typescript
// app/map/page.tsx
export default function MapLayout() {
  return (
    <div className="flex h-screen">
      {/* Left: Property list */}
      <div className="w-1/2 overflow-y-auto">
        <PropertyList />
      </div>

      {/* Right: Map */}
      <div className="w-1/2">
        <PropertyMap />
      </div>
    </div>
  );
}
```

---

## Next Steps

1. Create basic map component
2. Test with your 10 geocoded properties
3. Add clustering when you reach 50+ properties
4. Implement heatmap toggle
5. Add filter controls (price range, property type)

**Your data is ready** - all properties have lat/lng coordinates from Nominatim!
