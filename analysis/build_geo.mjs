// Project the land outline (world-atlas, Natural Earth) and tradition coordinates with a Pacific-centred Equal Earth projection.
// Usage: node build_geo.mjs <data.json> <geo.json>
import fs from 'fs';
import * as d3 from 'd3';
import { feature } from 'topojson-client';
const [,, dataPath, outPath] = process.argv;
const D = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const topo = JSON.parse(fs.readFileSync(new URL('./node_modules/world-atlas/land-110m.json', import.meta.url), 'utf8'));
const land = feature(topo, topo.objects.land);
const W = 1000;
const proj = d3.geoEqualEarth().rotate([-153, 0]).fitWidth(W, { type: 'Sphere' });
const yTop = proj([153, 82])[1], yBot = proj([153, -58])[1];
const path = d3.geoPath(proj).digits(1);
const gxy = D.g.lon.map((lon, i) => proj([lon, D.g.lat[i]]).map(v => Math.round(v * 10) / 10));
const sphere = path({ type: 'Sphere' });
const grat = d3.geoPath(proj).digits(1)(d3.geoGraticule().step([30, 30])());
const out = { W, y0: Math.round(yTop * 10) / 10, H: Math.round((yBot - yTop) * 10) / 10, land: path(land), sphere, grat, gxy };
fs.writeFileSync(outPath, JSON.stringify(out));
const ys = gxy.map(p => p[1]), xs = gxy.map(p => p[0]);
console.log('viewBox', out.y0, out.H, 'land path chars', out.land.length, 'x range', Math.min(...xs), Math.max(...xs), 'y range', Math.min(...ys), Math.max(...ys));
