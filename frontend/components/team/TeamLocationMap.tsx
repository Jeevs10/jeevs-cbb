"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { getCityCoordinates } from "@/lib/cityCoordinates";
import { useEffect } from "react";
import L from "leaflet";

interface TeamLocationMapProps {
  city?: string;
  state?: string;
  primaryColor?: string;
}

export default function TeamLocationMap({ city, state, primaryColor = "#000000" }: TeamLocationMapProps) {
  const coordinates = city && state ? getCityCoordinates(city, state) : null;

  useEffect(() => {
    // Fix for default marker icon in Leaflet with React
    if (typeof window !== "undefined") {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
      });
    }
  }, []);

  if (!coordinates) {
    return null;
  }

  // Create custom icon with team color (only on client)
  const customIcon = typeof window !== "undefined" ? new L.Icon({
    iconUrl: "data:image/svg+xml;base64," + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${primaryColor}" stroke="white" stroke-width="2">
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="3" fill="white" />
      </svg>
    `),
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  }) : undefined;

  return (
    <div className="w-full h-[400px] relative bg-[#e7e8d1] border-2 border-black">
      <style>{`
        .leaflet-container {
          background-color: #e7e8d1 !important;
        }
        .leaflet-popup-content-wrapper {
          background: #e7e8d1;
          border: 2px solid black;
          border-radius: 0;
          box-shadow: 3px 3px 0px rgba(0,0,0,1);
        }
        .leaflet-popup-tip {
          background: #e7e8d1;
          border: 2px solid black;
        }
        .leaflet-popup-content {
          font-family: monospace;
          margin: 8px 12px;
        }
        .natural-map {
          filter: saturate(1.1) brightness(1.05);
        }
      `}</style>
      <MapContainer
        center={[coordinates[0], coordinates[1]] as [number, number]}
        zoom={4}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="natural-map"
        />
        <Marker position={[coordinates[0], coordinates[1]] as [number, number]} icon={customIcon}>
          <Popup>
            <div className="font-mono text-sm">
              <strong>{city}, {state}</strong>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
