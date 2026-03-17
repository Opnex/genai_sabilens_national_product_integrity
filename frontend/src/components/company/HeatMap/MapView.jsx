import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from 'react-simple-maps';
import Card from '../../common/Card';

const NIGERIA_TOPO_URL =
  'https://raw.githubusercontent.com/deldersveld/topojson/master/countries/nigeria/nigeria-states.json';

const SEVERITY_CONFIG = {
  critical: { color: '#ef4444', glow: '#fca5a5', label: 'Critical', r: 7 },
  high:     { color: '#f97316', glow: '#fed7aa', label: 'High',     r: 6 },
  medium:   { color: '#3b82f6', glow: '#bfdbfe', label: 'Medium',   r: 5 },
  low:      { color: '#22c55e', glow: '#bbf7d0', label: 'Low',      r: 4 },
};

const STATE_DATA = [
  { name: 'Sokoto',      lon:  5.2476, lat: 13.0059, severity: 'medium',   reports: 65  },
  { name: 'Kebbi',       lon:  4.1975, lat: 11.4942, severity: 'low',      reports: 28  },
  { name: 'Zamfara',     lon:  6.2236, lat: 12.1704, severity: 'medium',   reports: 54  },
  { name: 'Katsina',     lon:  7.6014, lat: 12.9908, severity: 'high',     reports: 112 },
  { name: 'Kano',        lon:  8.5919, lat: 12.0022, severity: 'critical', reports: 278 },
  { name: 'Jigawa',      lon:  9.3557, lat: 12.1806, severity: 'medium',   reports: 67  },
  { name: 'Kaduna',      lon:  7.4381, lat: 10.5105, severity: 'high',     reports: 176 },
  { name: 'Yobe',        lon: 11.9488, lat: 12.2942, severity: 'medium',   reports: 58  },
  { name: 'Borno',       lon: 13.1571, lat: 11.8333, severity: 'medium',   reports: 76  },
  { name: 'Gombe',       lon: 11.1667, lat: 10.2792, severity: 'low',      reports: 34  },
  { name: 'Bauchi',      lon:  9.8442, lat: 10.3158, severity: 'low',      reports: 24  },
  { name: 'Adamawa',     lon: 12.3984, lat:  9.3265, severity: 'low',      reports: 29  },
  { name: 'Taraba',      lon: 11.3645, lat:  7.9994, severity: 'low',      reports: 22  },
  { name: 'Niger',       lon:  6.0008, lat: 10.0005, severity: 'low',      reports: 28  },
  { name: 'FCT',         lon:  7.3986, lat:  8.9928, severity: 'high',     reports: 143 },
  { name: 'Kwara',       lon:  4.5418, lat:  8.4799, severity: 'medium',   reports: 72  },
  { name: 'Kogi',        lon:  6.7397, lat:  7.4716, severity: 'medium',   reports: 88  },
  { name: 'Benue',       lon:  8.7965, lat:  7.3369, severity: 'medium',   reports: 95  },
  { name: 'Nassarawa',   lon:  8.4994, lat:  8.5494, severity: 'low',      reports: 41  },
  { name: 'Plateau',     lon:  9.2182, lat:  9.2182, severity: 'low',      reports: 32  },
  { name: 'Lagos',       lon:  3.3792, lat:  6.5244, severity: 'critical', reports: 312 },
  { name: 'Ogun',        lon:  3.3500, lat:  7.1600, severity: 'high',     reports: 134 },
  { name: 'Oyo',         lon:  3.9470, lat:  7.8500, severity: 'high',     reports: 198 },
  { name: 'Osun',        lon:  4.5624, lat:  7.5629, severity: 'low',      reports: 38  },
  { name: 'Ondo',        lon:  4.8400, lat:  7.2500, severity: 'medium',   reports: 67  },
  { name: 'Ekiti',       lon:  5.2180, lat:  7.7190, severity: 'low',      reports: 31  },
  { name: 'Enugu',       lon:  7.4951, lat:  6.4584, severity: 'medium',   reports: 98  },
  { name: 'Ebonyi',      lon:  8.0659, lat:  6.2649, severity: 'low',      reports: 27  },
  { name: 'Anambra',     lon:  6.7470, lat:  6.2100, severity: 'high',     reports: 154 },
  { name: 'Imo',         lon:  7.0498, lat:  5.4927, severity: 'low',      reports: 43  },
  { name: 'Abia',        lon:  7.5248, lat:  5.4527, severity: 'medium',   reports: 61  },
  { name: 'Edo',         lon:  5.6037, lat:  6.3350, severity: 'medium',   reports: 87  },
  { name: 'Delta',       lon:  5.8904, lat:  5.5000, severity: 'high',     reports: 132 },
  { name: 'Bayelsa',     lon:  6.3248, lat:  4.9268, severity: 'medium',   reports: 74  },
  { name: 'Rivers',      lon:  7.0134, lat:  4.8156, severity: 'critical', reports: 245 },
  { name: 'Cross River', lon:  8.3285, lat:  5.8702, severity: 'medium',   reports: 82  },
  { name: 'Akwa Ibom',   lon:  7.9306, lat:  5.0076, severity: 'high',     reports: 118 },
];

const STATE_SEVERITY = STATE_DATA.reduce((acc, s) => {
  acc[s.name.toLowerCase()] = s.severity;
  return acc;
}, {});

const ZONE_FILL = {
  critical: '#fee2e2',
  high:     '#ffedd5',
  medium:   '#dbeafe',
  low:      '#dcfce7',
  default:  '#e8f4e8',
};

const getStateFill = (geoName = '') => {
  const key = geoName.toLowerCase();
  if (STATE_SEVERITY[key]) return ZONE_FILL[STATE_SEVERITY[key]];
  const found = Object.keys(STATE_SEVERITY).find(k => key.includes(k) || k.includes(key));
  return found ? ZONE_FILL[STATE_SEVERITY[found]] : ZONE_FILL.default;
};

const MIN_ZOOM = 1;
const MAX_ZOOM = 6;
const ZOOM_STEP = 1.5;

const MapView = ({ onRegionSelect }) => {
  const [hoveredState, setHoveredState] = useState(null);
  const [hoveredGeo, setHoveredGeo]     = useState(null);
  const [zoom, setZoom]                 = useState(1);
  const [pan, setPan]                   = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging]     = useState(false);
  const dragStart                        = useRef(null);
  const panStart                         = useRef(null);
  const containerRef                     = useRef(null);

  const handleZoomIn  = () => setZoom(z => Math.min(+(z * ZOOM_STEP).toFixed(2), MAX_ZOOM));
  const handleZoomOut = () => setZoom(z => {
    const next = Math.max(+(z / ZOOM_STEP).toFixed(2), MIN_ZOOM);
    if (next === MIN_ZOOM) setPan({ x: 0, y: 0 });
    return next;
  });
  const handleReset   = () => { setZoom(1); setPan({ x: 0, y: 0 }); };

  // Wheel zoom
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    if (e.deltaY < 0) setZoom(z => Math.min(+(z * 1.2).toFixed(2), MAX_ZOOM));
    else              setZoom(z => {
      const next = Math.max(+(z / 1.2).toFixed(2), MIN_ZOOM);
      if (next === MIN_ZOOM) setPan({ x: 0, y: 0 });
      return next;
    });
  }, []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.addEventListener('wheel', handleWheel, { passive: false });
    return () => el.removeEventListener('wheel', handleWheel);
  }, [handleWheel]);

  // Drag to pan
  const handleMouseDown = (e) => {
    if (zoom <= 1) return;
    setIsDragging(true);
    dragStart.current = { x: e.clientX, y: e.clientY };
    panStart.current  = { ...pan };
  };
  const handleMouseMove = (e) => {
    if (!isDragging || !dragStart.current) return;
    const dx = e.clientX - dragStart.current.x;
    const dy = e.clientY - dragStart.current.y;
    setPan({ x: panStart.current.x + dx, y: panStart.current.y + dy });
  };
  const handleMouseUp = () => { setIsDragging(false); dragStart.current = null; };

  return (
    <Card className="h-[600px] relative overflow-hidden p-0">

      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 bg-white/95 backdrop-blur-sm rounded-xl shadow-soft p-3 border border-gray-100">
        <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Risk Level</p>
        {Object.entries(SEVERITY_CONFIG).map(([key, cfg]) => (
          <div key={key} className="flex items-center gap-2 text-xs mb-1.5 last:mb-0">
            <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: cfg.color }} />
            <span className="text-gray-600">{cfg.label}</span>
          </div>
        ))}
      </div>

      {/* Title */}
      <div className="absolute top-4 left-4 z-10">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Nigeria</p>
        <p className="text-sm font-bold text-gray-700">Counterfeit Risk Map</p>
      </div>

      {/* Zoom Controls */}
      <div className="absolute bottom-6 right-4 z-10 flex flex-col gap-1.5">
        <button
          onClick={handleZoomIn}
          className="w-9 h-9 bg-white border border-gray-200 rounded-xl shadow-soft flex items-center justify-center text-gray-700 hover:bg-primary hover:text-white hover:border-primary transition-all font-bold text-xl leading-none select-none"
        >+</button>
        <button
          onClick={handleZoomOut}
          className="w-9 h-9 bg-white border border-gray-200 rounded-xl shadow-soft flex items-center justify-center text-gray-700 hover:bg-primary hover:text-white hover:border-primary transition-all font-bold text-xl leading-none select-none"
        >−</button>
        <button
          onClick={handleReset}
          className="w-9 h-9 bg-white border border-gray-200 rounded-xl shadow-soft flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-all text-xs font-bold select-none"
          title="Reset view"
        >⊙</button>
      </div>

      {/* Zoom % */}
      <div className="absolute bottom-6 left-4 z-10 bg-white/80 border border-gray-100 rounded-lg px-2 py-1 pointer-events-none">
        <span className="text-xs text-gray-400 font-mono">{Math.round(zoom * 100)}%</span>
      </div>

      {/* Hover Tooltip */}
      {hoveredState && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-20 bg-white border border-gray-100 rounded-xl shadow-lg px-4 py-2 pointer-events-none whitespace-nowrap">
          <p className="text-xs font-bold text-gray-800">{hoveredState.name}</p>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: SEVERITY_CONFIG[hoveredState.severity].color }} />
            <span className="text-xs font-medium" style={{ color: SEVERITY_CONFIG[hoveredState.severity].color }}>
              {SEVERITY_CONFIG[hoveredState.severity].label}
            </span>
            <span className="text-xs text-gray-400 ml-1">{hoveredState.reports} reports</span>
          </div>
        </div>
      )}

      {/* Map container — CSS transform handles zoom + pan */}
      <div
        ref={containerRef}
        className="w-full h-full bg-gradient-to-br from-slate-50 to-blue-50/30 overflow-hidden"
        style={{ cursor: isDragging ? 'grabbing' : zoom > 1 ? 'grab' : 'default' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* This inner div is what gets scaled — transform-origin center */}
        <div
          style={{
            width: '100%',
            height: '100%',
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.25s ease',
            willChange: 'transform',
          }}
        >
          {/* Inject CSS so vector-effect hits actual SVG DOM elements */}
          <style>{`
            .rsm-state-fill path {
              vector-effect: non-scaling-stroke;
              stroke: #1e3a5f;
              stroke-width: 1px;
              cursor: pointer;
            }
            .rsm-state-fill path:hover {
              stroke: #0c1f3f;
              stroke-width: 1.5px;
            }
            .rsm-outer-border path {
              vector-effect: non-scaling-stroke;
              fill: none !important;
              stroke: #0c1f3f;
              stroke-width: 3px;
              stroke-linejoin: round;
              stroke-linecap: round;
              pointer-events: none;
            }
          `}</style>

          <ComposableMap
            projection="geoMercator"
            projectionConfig={{ center: [8.6753, 9.082], scale: 2800 }}
            style={{ width: '100%', height: '100%' }}
          >
            {/* ── State fills with inner borders via CSS class ── */}
            <Geographies geography={NIGERIA_TOPO_URL} className="rsm-state-fill">
              {({ geographies }) =>
                geographies.map((geo) => {
                  const geoName   = geo.properties.NAME_1 || geo.properties.name || '';
                  const stateData = STATE_DATA.find(s =>
                    geoName.toLowerCase().includes(s.name.toLowerCase()) ||
                    s.name.toLowerCase().includes(geoName.toLowerCase())
                  );
                  const isHovered = hoveredGeo === geo.rsmKey;
                  const fill      = getStateFill(geoName);

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      onMouseEnter={() => { setHoveredGeo(geo.rsmKey); if (stateData) setHoveredState(stateData); }}
                      onMouseLeave={() => { setHoveredGeo(null); setHoveredState(null); }}
                      onClick={() => { if (stateData && onRegionSelect) onRegionSelect(stateData.name); }}
                      style={{
                        default: { fill: isHovered ? '#dde6f5' : fill, outline: 'none' },
                        hover:   { fill: '#dde6f5', outline: 'none' },
                        pressed: { fill: '#c8d8ee', outline: 'none' },
                      }}
                    />
                  );
                })
              }
            </Geographies>

            {/* ── Outer national border — thick 3px via CSS, no fill, no pointer events ── */}
            <Geographies geography={NIGERIA_TOPO_URL} className="rsm-outer-border">
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey + '-outer'}
                    geography={geo}
                    style={{
                      default: { fill: 'none', outline: 'none' },
                      hover:   { fill: 'none', outline: 'none' },
                      pressed: { fill: 'none', outline: 'none' },
                    }}
                  />
                ))
              }
            </Geographies>

            {/* ── Hotspot markers — fixed pixel size via vectorEffect ── */}
            {STATE_DATA.map((state) => {
              const cfg       = SEVERITY_CONFIG[state.severity];
              const isHovered = hoveredState?.name === state.name;
              const r         = isHovered ? cfg.r + 2 : cfg.r;

              return (
                <Marker
                  key={state.name}
                  coordinates={[state.lon, state.lat]}
                  onMouseEnter={() => setHoveredState(state)}
                  onMouseLeave={() => setHoveredState(null)}
                  onClick={() => onRegionSelect && onRegionSelect(state.name)}
                >
                  {/* Glow halo */}
                  <circle
                    r={r + 4}
                    fill={cfg.glow}
                    opacity={isHovered ? 0.8 : 0.45}
                    style={{ vectorEffect: 'non-scaling-stroke' }}
                  />
                  {/* Pulse ring for critical */}
                  {state.severity === 'critical' && (
                    <circle
                      r={r + 9}
                      fill="none"
                      stroke={cfg.color}
                      strokeWidth="1.5"
                      opacity="0.3"
                      style={{ vectorEffect: 'non-scaling-stroke' }}
                    />
                  )}
                  {/* Core dot */}
                  <circle
                    r={r}
                    fill={cfg.color}
                    stroke="white"
                    strokeWidth="1.5"
                    style={{ cursor: 'pointer', vectorEffect: 'non-scaling-stroke' }}
                  />
                  {/* Label with white outline for legibility */}
                  <text
                    textAnchor="middle"
                    y={r + 10}
                    style={{
                      fontSize: '5px',
                      fontWeight: '700',
                      fill: '#0f172a',
                      pointerEvents: 'none',
                      userSelect: 'none',
                      paintOrder: 'stroke',
                      stroke: 'white',
                      strokeWidth: '2px',
                      strokeLinejoin: 'round',
                    }}
                  >
                    {state.name}
                  </text>
                </Marker>
              );
            })}
          </ComposableMap>
        </div>
      </div>
    </Card>
  );
};

export default MapView;