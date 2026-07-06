import { useMemo, useState } from "react"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import type { Facility } from "../../../types"
import { useFacilities } from "../../../hooks/useFacilities"

function normalizeFacility(raw: unknown, fallbackIndex: number): Facility | null {
  if (!raw || typeof raw !== "object") return null

  const candidate = raw as Record<string, unknown>
  const location = candidate.location as Record<string, unknown> | undefined

  const rawLat = candidate.lat ?? candidate.latitude ?? candidate.latitude_deg ?? location?.latitude
  const rawLng = candidate.lng ?? candidate.longitude ?? candidate.longitude_deg ?? location?.longitude

  const lat = typeof rawLat === "number" ? rawLat : Number(rawLat)
  const lng = typeof rawLng === "number" ? rawLng : Number(rawLng)

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null

  const id = String(candidate.id ?? candidate.facility_id ?? candidate.facilityId ?? `facility-${fallbackIndex}`)
  const name = String(candidate.name ?? candidate.facility_name ?? candidate.facilityName ?? `Facility ${fallbackIndex + 1}`)
  const type = (candidate.type ?? candidate.facility_type ?? "hospital") as Facility["type"]
  const status = (candidate.status ?? "stocked") as Facility["status"]
  const address = String(candidate.address ?? candidate.address_line ?? location?.address ?? "Bengaluru")

  return {
    id,
    name,
    type: type === "hospital" || type === "pharmacy" || type === "clinic" ? type : "hospital",
    lat,
    lng,
    status: status === "stocked" || status === "low" || status === "critical" || status === "emergency" ? status : "stocked",
    address,
  }
}

const fallbackFacilities: Facility[] = [
  {
    id: "fac-1",
    name: "Apollo Hospital",
    type: "hospital",
    lat: 12.9716,
    lng: 77.5946,
    status: "stocked",
    address: "Bengaluru",
  },
  {
    id: "fac-2",
    name: "Fortis BBT",
    type: "hospital",
    lat: 12.9555,
    lng: 77.6358,
    status: "critical",
    address: "Bengaluru",
  },
  {
    id: "fac-3",
    name: "Aster Supply Hub",
    type: "pharmacy",
    lat: 12.9300,
    lng: 77.6100,
    status: "low",
    address: "Bengaluru",
  },
  {
    id: "fac-4",
    name: "Manipal Pharmacy",
    type: "pharmacy",
    lat: 12.9165,
    lng: 77.5860,
    status: "emergency",
    address: "Bengaluru",
  },
]

const statusColor: Record<Facility["status"], string> = {
  stocked: "#16a34a",
  low: "#d97706",
  critical: "#ea580c",
  emergency: "#dc2626",
}

function createMarkerIcon(color: string) {
  return L.divIcon({
    html: `<div style="background:${color}; width:12px; height:12px; border-radius:9999px; border:2px solid white; box-shadow:0 0 0 2px ${color}22;"></div>`,
    className: "",
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  })
}

export function EmergencyMap() {
  const { data: facilities = [] } = useFacilities()
  const [selectedFacility, setSelectedFacility] = useState<Facility | null>(null)

  const facilityList = useMemo<Facility[]>(() => {
    if (Array.isArray(facilities) && facilities.length > 0) {
      const normalized = facilities
        .map((facility, index) => normalizeFacility(facility, index))
        .filter((item): item is Facility => Boolean(item))

      if (normalized.length > 0) return normalized
    }

    return fallbackFacilities
  }, [facilities])

  const activeFacility = selectedFacility ?? facilityList[0] ?? null

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Live Operations Map</h3>
          <p className="text-sm text-slate-500">Facility status and redistribution routes in real time.</p>
        </div>
        <div className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">Live</div>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
        <MapContainer center={[12.9716, 77.5946]} zoom={11} scrollWheelZoom className="h-[320px] w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {facilityList.map((facility) => (
            <Marker
              key={facility.id}
              position={[facility.lat, facility.lng]}
              icon={createMarkerIcon(statusColor[facility.status])}
              eventHandlers={{ click: () => setSelectedFacility(facility) }}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-semibold text-slate-900">{facility.name}</div>
                  <div className="text-slate-600">{facility.address}</div>
                  <div className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">{facility.status}</div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {activeFacility && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-900">{activeFacility.name}</p>
              <p className="text-sm text-slate-500">{activeFacility.address}</p>
            </div>
            <div className="rounded-full bg-white px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-slate-600">
              {activeFacility.status}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
