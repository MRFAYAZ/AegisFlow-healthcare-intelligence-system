import { useMemo, useState } from "react"
import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { useFacilities } from "../../../hooks/useFacilities"
import type { Emergency } from "../../../types/emergency"

interface Props {
  emergencies: Emergency[]
}

interface NetworkFacility {
  id: string
  name: string
  facilityType: string
  lat: number
  lng: number
  address: string
  active: boolean
  coldChainCapable: boolean
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
    coldChainCapable: candidate.cold_chain_capable === true,
  }
}

function createFacilityIcon(active: boolean) {
  const color = active ? "#2563eb" : "#64748b"
  return L.divIcon({
    html: `<div style="background:${color}; width:13px; height:13px; border-radius:9999px; border:2px solid white; box-shadow:0 0 0 2px ${color}22;"></div>`,
    className: "",
    iconSize: [13, 13],
    iconAnchor: [6, 6],
  })
}

function createIncidentIcon(severity: string) {
  const color = severity === "EMERGENCY" ? "#b91c1c" : severity === "CRITICAL" ? "#ea580c" : "#d97706"
  const size = severity === "EMERGENCY" ? 17 : 15
  return L.divIcon({
    html: `<div style="background:${color}; width:${size}px; height:${size}px; border-radius:9999px; border:3px solid white; box-shadow:0 0 0 3px ${color}33;"></div>`,
    className: "",
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function validCoordinatePair(latitude?: number | null, longitude?: number | null): latitude is number {
  return latitude !== null && latitude !== undefined
    && longitude !== null && longitude !== undefined
    && Number.isFinite(latitude) && latitude >= -90 && latitude <= 90
    && Number.isFinite(longitude) && longitude >= -180 && longitude <= 180
}

export function EmergencyMap({ emergencies }: Props) {
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

  const geocodedEmergencies = emergencies.filter((emergency) =>
    validCoordinatePair(emergency.facility_latitude, emergency.facility_longitude)
  )

  const transfersInMotion = emergencies.filter((emergency) =>
    (emergency.transfer_status === "IN_TRANSIT" || emergency.dispatch_status === "IN_TRANSIT")
    && validCoordinatePair(emergency.facility_latitude, emergency.facility_longitude)
    && validCoordinatePair(emergency.donor_latitude, emergency.donor_longitude)
  )

  const initialFacility = facilities[0]
  const initialEmergency = geocodedEmergencies[0]
  const center: [number, number] = initialFacility
    ? [initialFacility.lat, initialFacility.lng]
    : initialEmergency
      ? [initialEmergency.facility_latitude!, initialEmergency.facility_longitude!]
      : [13.0827, 80.2707]

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Live facility network & emergency incidents</h3>
          <p className="text-sm text-slate-500">
            Registered facility coordinates, geocoded shortages and transfers currently in transit.
          </p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">Backend data</span>
      </div>

      <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-600">
        <Legend color="#2563eb" label="Active facility" />
        <Legend color="#64748b" label="Inactive facility" />
        <Legend color="#b91c1c" label="Emergency incident" />
        <Legend color="#ea580c" label="Critical incident" />
        <Legend color="#0ea5e9" label="Transfer connector" />
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
            Add valid latitude and longitude values to registered facility locations to populate the network map.
          </p>
        </div>
      )}

      {!isLoading && !isError && facilities.length > 0 && (
        <>
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
            <MapContainer
              key={facilities[0].id}
              center={center}
              zoom={11}
              scrollWheelZoom
              className="h-[360px] w-full"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {transfersInMotion.map((emergency) => (
                <Polyline
                  key={`route-${emergency.emergency_case_id}`}
                  positions={[
                    [emergency.donor_latitude!, emergency.donor_longitude!],
                    [emergency.facility_latitude!, emergency.facility_longitude!],
                  ]}
                  pathOptions={{ color: "#0ea5e9", weight: 3, opacity: 0.85, dashArray: "6 7" }}
                />
              ))}

              {facilities.map((facility) => (
                <Marker
                  key={facility.id}
                  position={[facility.lat, facility.lng]}
                  icon={createFacilityIcon(facility.active)}
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
                      <div className="mt-1 text-xs text-slate-600">
                        Cold-chain capability: {facility.coldChainCapable ? "Declared" : "Not declared"}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {geocodedEmergencies.map((emergency) => (
                <Marker
                  key={`incident-${emergency.emergency_case_id}`}
                  position={[emergency.facility_latitude!, emergency.facility_longitude!]}
                  icon={createIncidentIcon(emergency.severity)}
                >
                  <Popup>
                    <div className="min-w-[180px] text-sm">
                      <div className="font-semibold text-slate-900">{emergency.medicine_name} shortage</div>
                      <div className="text-slate-600">{emergency.facility_name}</div>
                      <div className="mt-1 font-medium">{emergency.severity} · {emergency.emergency_status.replaceAll("_", " ")}</div>
                      <div className="mt-1 text-slate-600">
                        Remaining target: {Math.max(0, emergency.required_quantity - emergency.available_quantity)} units
                      </div>
                      {emergency.donor_facility && (
                        <div className="mt-1 text-slate-600">Current donor: {emergency.donor_facility}</div>
                      )}
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
            <NetworkMetric label="Active facilities plotted" value={facilities.filter((facility) => facility.active).length} />
            <NetworkMetric label="Emergency cases shown" value={geocodedEmergencies.length} />
            <NetworkMetric label="Transfers in transit" value={transfersInMotion.length} />
            <NetworkMetric label="Cold-chain capable facilities" value={facilities.filter((facility) => facility.coldChainCapable).length} />
          </div>

          {emergencies.length > geocodedEmergencies.length && (
            <p className="mt-3 text-xs text-amber-700">
              {emergencies.length - geocodedEmergencies.length} emergency case(s) lack usable coordinates and are omitted from the map, but remain visible in the incident list.
            </p>
          )}

          <p className="mt-3 text-xs text-slate-500">
            Donor-to-recipient connectors are straight lines between stored coordinates, not road routes or travel-time estimates.
          </p>

          {selectedFacility && (
            <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">{selectedFacility.name}</p>
                  <p className="text-sm text-slate-500">{selectedFacility.address}</p>
                  <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{selectedFacility.facilityType}</p>
                  <p className="mt-1 text-xs text-slate-600">
                    Cold-chain capability: {selectedFacility.coldChainCapable ? "Declared" : "Not declared"}
                  </p>
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

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  )
}

function NetworkMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  )
}
