import { useState } from "react"
import { MapContainer, Marker, Popup, TileLayer, Polyline } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import type { Emergency } from "../../../types/emergency"
// Import the new hook to fetch all facilities
import { useFacilities } from "../../../hooks/useFacilities"

// Helper function to assign colors based on facility type
function getFacilityColor(type: string) {
  switch (type?.toUpperCase()) {
    case "HOSPITAL": return "#2563eb" // Blue
    case "PHARMACY": return "#9333ea" // Purple
    case "SUPPLIER": return "#f97316" // Orange
    default: return "#94a3b8"         // Slate
  }
}

function createMarkerIcon(color: string) {
  return L.divIcon({
    html: `<div style="background:${color}; width:12px; height:12px; border-radius:9999px; border:2px solid white; box-shadow:0 0 0 2px ${color}22;"></div>`,
    className: "",
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  })
}

interface EmergencyMapProps {
  emergencies: Emergency[]
}

export function EmergencyMap({ emergencies }: EmergencyMapProps) {
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>(null)

  // Fetch the full healthcare network
  const { data: facilities = [] } = useFacilities()

  const emergencyMarkers = emergencies
    .filter(
      (e) =>
        e.facility_latitude != null &&
        e.facility_longitude != null
    )
    .map((e) => ({
      id: e.emergency_case_id,
      hospital: e.facility_name,
      medicine: e.medicine_name,
      severity: e.severity,
      lat: e.facility_latitude!,
      lng: e.facility_longitude!,
      donorLat: e.donor_latitude,
      donorLng: e.donor_longitude,
      donor: e.donor_facility,
      status: e.transfer_status,
    }))

  const activeIncident = emergencyMarkers.find((e) => e.id === activeIncidentId) ?? emergencyMarkers[0] ?? null

  return (
    <div className="rounded-2xl border border-border bg-surface-base p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-ink">Live Healthcare Network</h3>
          <p className="text-sm text-ink-muted">Live network tracking and AI redistribution routes.</p>
        </div>
        <div className="rounded-full bg-surface-subtle px-3 py-1 text-sm font-medium text-ink-muted">Live</div>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
        <MapContainer center={[13.0827, 80.2707]} zoom={11} scrollWheelZoom className="h-[320px] w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* 1. Base Layer: All Network Facilities */}
          {facilities.map((f: any) => (
            f.latitude && f.longitude ? (
              <Marker
                key={f.facility_id}
                position={[f.latitude, f.longitude]}
                icon={createMarkerIcon(getFacilityColor(f.facility_type))}
              >
                <Popup>
                  <div>
                    <h4 className="font-semibold text-ink">{f.facility_name}</h4>
                    <p className="text-sm text-ink-muted">{f.facility_type}</p>
                  </div>
                </Popup>
              </Marker>
            ) : null
          ))}

          {/* 2. Delivery Routes (Polylines) */}
          {emergencyMarkers.map((e) =>
            e.donorLat != null && e.donorLng != null ? (
              <Polyline
                key={`${e.id}-route`}
                positions={[
                  [e.donorLat, e.donorLng],
                  [e.lat, e.lng],
                ]}
                pathOptions={{
                  color: "#2563eb",
                  weight: 3,
                  dashArray: e.status === "PENDING" ? "5, 10" : undefined, 
                }}
              />
            ) : null
          )}

          {/* 3. Selected Donor Markers (Overlays Base Facility) */}
          {emergencyMarkers.map((e) =>
            e.donorLat != null && e.donorLng != null ? (
              <Marker
                key={`${e.id}-donor`}
                position={[e.donorLat, e.donorLng]}
                icon={createMarkerIcon("#16a34a")} 
                eventHandlers={{ click: () => setActiveIncidentId(e.id) }}
              >
                <Popup>
                  <div>
                    <h4 className="font-semibold text-ink">{e.donor}</h4>
                    <p className="text-sm text-ink-muted">Selected Donor</p>
                  </div>
                </Popup>
              </Marker>
            ) : null
          )}

          {/* 4. Emergency Incidents Markers (Overlays Base Facility) */}
          {emergencyMarkers.map((e) => (
            <Marker
              key={e.id}
              position={[e.lat, e.lng]}
              icon={createMarkerIcon("#dc2626")} 
              eventHandlers={{ click: () => setActiveIncidentId(e.id) }}
            >
              <Popup>
                <div>
                  <h4 className="font-semibold">{e.hospital}</h4>
                  <p>{e.medicine}</p>
                  <p className="text-red-600 font-medium">{e.severity}</p>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {activeIncident && (
        <div className="mt-4 rounded-xl border border-border bg-surface-muted p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-ink">{activeIncident.hospital}</p>
              <p className="text-sm text-ink-muted">
                Needs: <span className="font-medium text-ink">{activeIncident.medicine}</span>
                {activeIncident.donor && ` • Donor: ${activeIncident.donor}`}
              </p>
            </div>
            <div className="rounded-full bg-surface-base px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-ink-muted border border-border shadow-sm">
              {activeIncident.severity}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}