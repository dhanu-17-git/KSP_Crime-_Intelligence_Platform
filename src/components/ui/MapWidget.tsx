import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export interface MapMarker {
  id: string;
  position: [number, number];
  title: string;
  description: string;
  severity?: 'Critical' | 'Major' | 'Moderate' | 'Minor';
  onClick?: () => void;
}

interface MapWidgetProps {
  center: [number, number];
  zoom: number;
  markers: MapMarker[];
  height?: string;
  showHeatmap?: boolean;
}

export const MapWidget: React.FC<MapWidgetProps> = ({ center, zoom, markers, height = '350px', showHeatmap = false }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markerGroupRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Create the map instance if not already initialized
    if (!mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, {
        zoomControl: true,
        scrollWheelZoom: true,
      }).setView(center, zoom);

      // CartoDB Positron - Light Theme Map layer matching MS Fluent/SAP visual aesthetic
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(mapInstance.current);

      markerGroupRef.current = L.layerGroup().addTo(mapInstance.current);
    } else {
      mapInstance.current.setView(center, zoom);
    }

    // Update markers on change
    if (markerGroupRef.current && mapInstance.current) {
      markerGroupRef.current.clearLayers();

      markers.forEach((m) => {
        // Color code markers based on severity
        let color = '#0f1e36'; // Navy default
        let border = '#b89020'; // Gold border
        let pulseClass = '';
        if (m.severity === 'Critical') {
          color = '#b91c1c'; // Crimson
          border = '#fee2e2';
          pulseClass = 'pulse-marker-critical';
        } else if (m.severity === 'Major') {
          color = '#d97706'; // Amber
          border = '#fef3c7';
          pulseClass = 'pulse-marker-major';
        }

        const divIcon = L.divIcon({
          className: 'custom-map-pin',
          html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2.5px solid ${border}; transition: transform 0.2s;" class="hover:scale-125 ${pulseClass}"></div>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
          popupAnchor: [0, -7]
        });

        const marker = L.marker(m.position, { icon: divIcon })
          .bindPopup(`
            <div style="font-family: inherit; font-size: 11px; padding: 2px;">
              <b style="color: #0f1e36; font-size: 12px;">${m.title}</b>
              <div style="margin-top: 4px; color: #475569;">${m.description}</div>
              <div style="margin-top: 6px; font-weight: 600; font-size: 9px; text-transform: uppercase; color: #b89020;">Click node to view folder</div>
            </div>
          `);

        if (m.onClick) {
          marker.on('click', () => {
            m.onClick?.();
          });
        }

        if (showHeatmap) {
          const radius = m.severity === 'Critical' ? 1000 : m.severity === 'Major' ? 700 : 400;
          const circleColor = m.severity === 'Critical' ? '#b91c1c' : m.severity === 'Major' ? '#d97706' : '#b89020';
          const circle = L.circle(m.position, {
            color: circleColor,
            fillColor: circleColor,
            fillOpacity: 0.12,
            weight: 1,
            radius: radius
          });
          markerGroupRef.current?.addLayer(circle);
        }

        markerGroupRef.current?.addLayer(marker);
      });
    }
  }, [center, zoom, markers, showHeatmap]);

  // Clean up on component destroy
  useEffect(() => {
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  return (
    <div
      ref={mapRef}
      style={{ height }}
      className="w-full rounded-lg overflow-hidden border border-slate-200 shadow-sm relative z-10"
    />
  );
};
export default MapWidget;
