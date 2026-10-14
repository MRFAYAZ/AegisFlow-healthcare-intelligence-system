import { useMemo, useState } from "react"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { useFacilities } from "../../../hooks/useFacilities"

interface NetworkFacility {
  id: string
  name: string
  facilityType: string
  lat: number
  lng: number
  address: string
  active: boolean
}

function normalizeFacility(raw: unknown): NetworkFacility | null {
  if (!raw || typeof raw !== "object") return null

  const candidate = raw as Record<string, unknown>
  const rawLat = candidate.latitude ?? candidate.lat
  const rawLng = candidate.longitude ?? candidate.lng
  const lat = typeof rawLat === "number" ? rawLat : Number(rawLat)
  const lng = typeof rawLng === "number" ? rawLng : Number(rawLng)

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null

  const type = String(candidate.facility_type ?? candidate.type ?? "UNKNOWN")
  const addressParts = [
    candidate.address_line,
    candidate.city,
    candidate.state,
  ].filter((part): part is string => typeof part === "string" && part.trim().length > 0)

  return {
    id: String(candidate.facility_id ?? candidate.id),
    name: String(candidate.facility_name ?? candidate.name ?? "Unnamed facility"),
    facilityType: type.replaceAll("_", " "),
    lat,
    lng,
    address: addressParts.join(", ") || "Address not provided",
    active: candidate.is_active !== false,
  }
}

function createMarkerIcon(active: boolean) {
  const color = active ? "#2563eb" : "#64748b"
  return L.divIcon({
    html: `<div style="background:${color}; width:13px; height:13px; border-radius:9999px; border:2px solid white; box-shadow:0 0 0 2px ${color}22;"></div>`,
    className: "",
    iconSize: [13, 13],
    iconAnchor: [6, 6],
  })
}

export function EmergencyMap() {
  const { data: facilitiesData = [], isLoading, isError } = useFacilities()
  const [selectedFacilityId, setSelectedFacilityId] = useState<string | null>(null)

  const facilities = useMemo<NetworkFacility[]>(() => {
    if (!Array.isArray(facilitiesData)) return []
    return facilitiesData
      .map(normalizeFacility)
      .filter((item): item is NetworkFacility => item !== null)
  }, [facilitiesData])

  const selectedFacility =
    facilities.find((facility) => facility.id === selectedFacilityId) ??
    facilities[0] ??
    null

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Healthcare facility network</h3>
          <p className="text-sm text-slate-500">
            Registered facilities plotted from database coordinates.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          Backend data
        </span>
      </div>

      {isLoading && (
        <div className="mt-4 rounded-xl bg-slate-50 p-6 text-sm text-slate-500">
          Loading registered facility locations…
        </div>
      )}

      {isError && (
        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          Facility locations could not be loaded. The map is not displaying sample facilities.
        </div>
      )}

      {!isLoading && !isError && facilities.length === 0 && (
        <div className="mt-4 rounded-xl border border-dashed border-slate-300 p-6 text-center">
          <p className="font-semibold text-slate-800">No geocoded facilities available</p>
          <p className="mt-1 text-sm text-slate-500">
            Add valid latitude and longitude values to facility location records to populate this map.
          </p>
        </div>
      )}

      {!isLoading && !isError && facilities.length > 0 && (
        <>
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
            <MapContainer
              key={facilities[0].id}
              center={[facilities[0].lat, facilities[0].lng]}
              zoom={11}
              scrollWheelZoom
              className="h-[320px] w-full"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {facilities.map((facility) => (
                <Marker
                  key={facility.id}
                  position={[facility.lat, facility.lng]}
                  icon={createMarkerIcon(facility.active)}
                  eventHandlers={{ click: () => setSelectedFacilityId(facility.id) }}
                >
                  <Popup>
                    <div className="text-sm">
                      <div className="font-semibold text-slate-900">{facility.name}</div>
                      <div className="text-slate-600">{facility.facilityType}</div>
                      <div className="text-slate-600">{facility.address}</div>
                      <div className="mt-1 text-xs uppercase tracking-wide text-slate-500">
                        {facility.active ? "Active" : "Inactive"}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>

          {selectedFacility && (
            <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{selectedFacility.name}</p>
                  <p className="text-sm text-slate-500">{selectedFacility.address}</p>
                  <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{selectedFacility.facilityType}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${selectedFacility.active ? "bg-blue-100 text-blue-800" : "bg-slate-200 text-slate-700"}`}>
                  {selectedFacility.active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  )
}
