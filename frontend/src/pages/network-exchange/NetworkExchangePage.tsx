import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, ArrowUpRight, Check, Clock3, LoaderCircle, MapPin, Network, PackageSearch, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'
import { medicinesAPI, networkExchangeAPI } from '../../services/api'
import { useAppStore } from '../../store/useAppStore'

type Facility = {
  facility_id: string
  facility_name: string
  facility_type: string
  is_active: boolean
  network_visibility_enabled: boolean
}

type Medicine = {
  medicine_id: string
  medicine_name: string
  strength?: string | null
  dosage_form?: string | null
}

type NetworkOffer = {
  facility_id: string
  facility_name: string
  facility_type: string
  safe_transferable_quantity: number
  distance_km: number
  score: number
  batch_traceability_available: boolean
  cold_chain_eligible: boolean
  recommendation_reason: string
}

const DEMO_FACILITIES: Facility[] = [
  { facility_id: 'demo-city-general', facility_name: 'City General Hospital', facility_type: 'HOSPITAL', is_active: true, network_visibility_enabled: true },
  { facility_id: 'demo-east-care', facility_name: 'East Care Medical Center', facility_type: 'CLINIC', is_active: true, network_visibility_enabled: true },
  { facility_id: 'demo-north-supply', facility_name: 'North Supply Hub', facility_type: 'SUPPLIER', is_active: true, network_visibility_enabled: false },
  { facility_id: 'demo-west-pharmacy', facility_name: 'West Pharmacy Network', facility_type: 'PHARMACY', is_active: true, network_visibility_enabled: true },
]

const DEMO_MEDICINES: Medicine[] = [
  { medicine_id: 'demo-ampicillin', medicine_name: 'Ampicillin', strength: '500mg', dosage_form: 'Injection' },
  { medicine_id: 'demo-oxycodone', medicine_name: 'Oxycodone', strength: '10mg', dosage_form: 'Tablet' },
  { medicine_id: 'demo-insulin', medicine_name: 'Insulin Glargine', strength: '100U/ml', dosage_form: 'Injection' },
]

const DEMO_OFFERS: NetworkOffer[] = [
  {
    facility_id: 'demo-east-care',
    facility_name: 'East Care Medical Center',
    facility_type: 'CLINIC',
    safe_transferable_quantity: 180,
    distance_km: 12.1,
    score: 94.2,
    batch_traceability_available: true,
    cold_chain_eligible: true,
    recommendation_reason: 'Demo match: sufficient stock, traceable batches, and short-haul delivery support.',
  },
  {
    facility_id: 'demo-west-pharmacy',
    facility_name: 'West Pharmacy Network',
    facility_type: 'PHARMACY',
    safe_transferable_quantity: 130,
    distance_km: 21.4,
    score: 86.8,
    batch_traceability_available: true,
    cold_chain_eligible: true,
    recommendation_reason: 'Demo match: good fulfillment overlap with cold-chain capacity and moderate proximity.',
  },
  {
    facility_id: 'demo-north-supply',
    facility_name: 'North Supply Hub',
    facility_type: 'SUPPLIER',
    safe_transferable_quantity: 220,
    distance_km: 34.9,
    score: 78.6,
    batch_traceability_available: true,
    cold_chain_eligible: false,
    recommendation_reason: 'Demo match: high availability but cold-chain constraints mean it needs operational review.',
  },
]

export function NetworkExchangePage() {
  const user = useAppStore((state) => state.user)
  const queryClient = useQueryClient()
  const facilities = useQuery<Facility[]>({
    queryKey: ['network-facilities'],
    queryFn: async () => (await networkExchangeAPI.getAccessibleFacilities()).data,
  })
  const medicines = useQuery<Medicine[]>({
    queryKey: ['network-medicines'],
    queryFn: async () => (await medicinesAPI.getAll()).data,
  })
  const demoMode = facilities.isError || medicines.isError
  const effectiveFacilities = facilities.data ?? DEMO_FACILITIES
  const effectiveMedicines = medicines.data ?? DEMO_MEDICINES
  const activeFacilities = effectiveFacilities.filter((facility) => facility.is_active)
  const [facilityId, setFacilityId] = useState('')
  const [medicineId, setMedicineId] = useState('')
  const [quantity, setQuantity] = useState(100)
  const [radius, setRadius] = useState(50)
  const [emergencyOverride, setEmergencyOverride] = useState(false)
  const [offers, setOffers] = useState<NetworkOffer[] | null>(null)

  useEffect(() => {
    if (facilityId || !activeFacilities.length) return
    const preferred = activeFacilities.find((facility) => facility.facility_name === user?.facility)
    setFacilityId(preferred?.facility_id ?? activeFacilities[0].facility_id)
  }, [activeFacilities, facilityId, user?.facility])

  useEffect(() => {
    if (!medicineId && effectiveMedicines.length) setMedicineId(effectiveMedicines[0].medicine_id)
  }, [medicineId, effectiveMedicines])

  const selectedFacility = activeFacilities.find((facility) => facility.facility_id === facilityId)
  const visibilityMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      if (demoMode) {
        return { facility_id: facilityId, network_visibility_enabled: enabled }
      }
      return networkExchangeAPI.setVisibility(facilityId, enabled)
    },
    onSuccess: () => {
      toast.success(demoMode ? 'Demo visibility preference updated' : 'Network visibility preference updated')
      queryClient.invalidateQueries({ queryKey: ['network-facilities'] })
    },
    onError: () => toast.error('Could not update visibility. Confirm your facility access.'),
  })
  const searchMutation = useMutation({
    mutationFn: async () => {
      if (demoMode) {
        return DEMO_OFFERS.filter((offer) => offer.distance_km <= radius && offer.safe_transferable_quantity >= Math.min(25, quantity / 2))
          .map((offer) => ({ ...offer, score: Number((offer.score * 0.94).toFixed(1)) }))
      }

      return (await networkExchangeAPI.search({
        requester_facility_id: facilityId,
        medicine_id: medicineId,
        required_quantity: quantity,
        radius_km: radius,
        emergency_override: emergencyOverride,
      })).data as NetworkOffer[]
    },
    onSuccess: (result) => setOffers(result),
    onError: () => toast.error('Could not search the network. Confirm facility access and try again.'),
  })

  const role = user?.role
  const canOverride = role === 'emergency_operator' || role === 'system_admin'
  const loading = facilities.isLoading || medicines.isLoading
  const directoryError = facilities.isError || medicines.isError

  return (
    <div className="page-enter mx-auto max-w-6xl space-y-6 pb-10">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-brand-600">
            <Network size={15} /> Cross-organization coordination
          </div>
          <h1 className="text-2xl font-semibold text-ink">Network Exchange</h1>
          <p className="mt-1 max-w-2xl text-sm text-ink-muted">Discover request-relevant supply across participating facilities without exposing their full inventory.</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-ink-muted"><ShieldCheck size={16} className="text-status-green" /> Human approval required for every transfer</div>
      </header>

      <section className="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
        <div className="panel space-y-4">
          <div className="flex items-start gap-3 border-b border-border pb-4">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-status-blue-bg text-status-blue"><PackageSearch size={18} /></div>
            <div><h2 className="panel-title">Find eligible supply</h2><p className="mt-1 text-xs text-ink-muted">Ranked by fulfillment capacity and proximity, independent of facility ownership.</p></div>
          </div>
          {loading ? <div className="flex items-center gap-2 py-6 text-sm text-ink-muted"><LoaderCircle size={16} className="animate-spin" /> Loading network directory...</div> : directoryError ? <div role="alert" className="flex flex-wrap items-center justify-between gap-3 py-5"><p className="text-sm text-status-red">The live directory is unavailable, so the page is using a demo network view.</p><button className="btn btn-ghost" onClick={() => { void facilities.refetch(); void medicines.refetch() }}>Retry live data</button></div> : (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                <label><span className="f-label">Requesting facility</span><select className="f-input" value={facilityId} onChange={(event) => { setFacilityId(event.target.value); setOffers(null) }}><option value="">Select facility</option>{activeFacilities.map((facility) => <option key={facility.facility_id} value={facility.facility_id}>{facility.facility_name}</option>)}</select></label>
                <label><span className="f-label">Medicine</span><select className="f-input" value={medicineId} onChange={(event) => { setMedicineId(event.target.value); setOffers(null) }}><option value="">Select medicine</option>{effectiveMedicines.map((medicine) => <option key={medicine.medicine_id} value={medicine.medicine_id}>{medicine.medicine_name}{medicine.strength ? ` · ${medicine.strength}` : ''}</option>)}</select></label>
                <label><span className="f-label">Required quantity</span><input className="f-input" type="number" min={1} value={quantity} onChange={(event) => setQuantity(Math.max(1, Number(event.target.value)))} /></label>
                <label><span className="f-label">Search radius</span><select className="f-input" value={radius} onChange={(event) => setRadius(Number(event.target.value))}><option value={10}>10 km</option><option value={25}>25 km</option><option value={50}>50 km</option><option value={100}>100 km</option><option value={250}>250 km</option></select></label>
              </div>
              {canOverride && <label className="flex items-center gap-2 border-t border-border pt-3 text-xs text-ink-muted"><input type="checkbox" checked={emergencyOverride} onChange={(event) => { setEmergencyOverride(event.target.checked); setOffers(null) }} /> Emergency visibility override <span className="text-status-red">(audited)</span></label>}
              <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
                <p className="max-w-lg text-[11px] leading-5 text-ink-faint">Offers account for donor safety stock, eligible batch expiry/status, cold-chain capability, and distance. Search does not reserve stock.</p>
                <button className="btn btn-primary" disabled={!facilityId || !medicineId || searchMutation.isPending} onClick={() => searchMutation.mutate()}><PackageSearch size={15} />{searchMutation.isPending ? 'Searching...' : 'Search network'}</button>
              </div>
            </>
          )}
        </div>

        <aside className="flex flex-col justify-between gap-4 border-l-2 border-brand-500 bg-surface-subtle p-5">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-ink"><Activity size={16} className="text-brand-600" /> Controlled availability</div>
            <p className="mt-2 text-xs leading-5 text-ink-muted">Your facility stays private until an authorized member opts into network discovery. Only safe transferable availability is returned for a specific request.</p>
          </div>
          <div>
            <div className="mb-3 flex items-center justify-between gap-2"><div><div className="text-xs font-semibold text-ink">{selectedFacility?.facility_name ?? 'Select a facility'}</div><div className="text-[10px] text-ink-faint">{selectedFacility?.network_visibility_enabled ? 'Visible to standard network searches' : 'Hidden from standard network searches'}</div></div><span className={`badge ${selectedFacility?.network_visibility_enabled ? 'badge-green' : 'badge-yellow'}`}>{selectedFacility?.network_visibility_enabled ? 'Opted in' : 'Private'}</span></div>
            <button className="btn btn-ghost w-full justify-center" disabled={!facilityId || visibilityMutation.isPending} onClick={() => visibilityMutation.mutate(!selectedFacility?.network_visibility_enabled)}>{visibilityMutation.isPending ? <LoaderCircle size={14} className="animate-spin" /> : <Check size={14} />}{selectedFacility?.network_visibility_enabled ? 'Disable network visibility' : 'Enable network visibility'}</button>
            <p className="mt-2 text-[10px] leading-4 text-ink-faint">Visibility changes are audited. Emergency operators may request an audited override; safety checks still apply.</p>
          </div>
        </aside>
      </section>

      <section className="panel overflow-hidden p-0">
        <div className="flex items-center justify-between border-b border-border px-5 py-4"><div><h2 className="panel-title">Eligible source offers</h2><p className="mt-1 text-xs text-ink-muted">{offers ? `${offers.length} eligible ${offers.length === 1 ? 'source' : 'sources'} for this request` : 'Run a search to compare available sources.'}</p></div><Clock3 size={17} className="text-ink-faint" /></div>
        {offers === null ? <div className="py-12 text-center text-sm text-ink-faint">Offers will appear here. Facility-wide stock details remain private.</div> : offers.length === 0 ? <div className="py-12 text-center text-sm text-ink-muted">No eligible sources found within this request's safety and distance limits.</div> : <div className="overflow-x-auto"><table className="af-table"><thead><tr><th>Source</th><th>Safe quantity</th><th>Distance</th><th>Score</th><th>Safety</th><th>Basis</th></tr></thead><tbody>{offers.map((offer, index) => <tr key={offer.facility_id}><td><div className="flex items-center gap-2 font-semibold text-ink">{index === 0 && <span className="badge badge-green">Top match</span>}{offer.facility_name}</div><div className="mt-1 text-[10px] text-ink-faint">{offer.facility_type.replaceAll('_', ' ')}</div></td><td className="font-semibold text-ink">{offer.safe_transferable_quantity.toLocaleString()} units</td><td><span className="inline-flex items-center gap-1"><MapPin size={12} />{offer.distance_km.toFixed(1)} km</span></td><td><strong className="text-brand-600">{offer.score.toFixed(1)}</strong><div className="mt-1 h-1 w-20 overflow-hidden rounded bg-surface-subtle"><div className="h-full bg-brand-500" style={{ width: `${Math.min(offer.score, 100)}%` }} /></div></td><td><div className="text-[10px]">{offer.batch_traceability_available ? 'Batch traceable' : 'No batch trace'}</div><div className="text-[10px] text-ink-faint">{offer.cold_chain_eligible ? 'Cold-chain eligible' : 'Cold-chain unavailable'}</div></td><td className="max-w-xs text-[11px]">{offer.recommendation_reason}</td></tr>)}</tbody></table></div>}
      </section>

      <div className="flex items-start gap-2 px-1 text-[11px] leading-5 text-ink-faint"><ArrowUpRight size={14} className="mt-0.5 flex-shrink-0" /> Recommendations are informational. A hospital administrator approves proposed allocations; reservation, dispatch, delivery, and settlement continue through their existing workflows.</div>
    </div>
  )
}