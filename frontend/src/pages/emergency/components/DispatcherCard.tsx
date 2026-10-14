import { Badge } from "../../../components/ui/Badge"
import type { Emergency } from "../../../types/emergency"

interface Props{
    emergency:Emergency
}

export function DispatcherCard({

    emergency

}:Props){

    if(!emergency.transfer_id){

        return(

            <div className="rounded-xl border bg-white p-5">

                <h3 className="font-semibold">

                    Dispatcher

                </h3>

                <p className="mt-3 text-slate-500">

                    Waiting for donor approval...

                </p>

            </div>

        )

    }

    const eta=Math.round(
        (emergency.transfer_distance_km ?? 5)*2
    )

    return(

        <div className="rounded-xl border bg-white p-5">

            <div className="flex justify-between">

                <div>

                    <h3 className="font-semibold text-lg">

                        Dispatcher Console

                    </h3>

                    <p className="text-sm text-slate-500">

                        Transfer

                        #{emergency.transfer_id.slice(0,8)}

                    </p>

                </div>

                <Badge variant="blue">

                    {emergency.transfer_status}

                </Badge>

            </div>

            <div className="grid grid-cols-2 gap-3 mt-5">

                <Stat
                    title="Donor"

                    value={
                        emergency.donor_facility ?? "-"
                    }
                />

                <Stat
                    title="Destination"

                    value={
                        emergency.facility_name
                    }
                />

                <Stat
                    title="Medicine"

                    value={
                        emergency.medicine_name
                    }
                />

                <Stat
                    title="Units"

                    value={
                        String(
                            emergency.approved_quantity ?? 0
                        )
                    }
                />

                <Stat
                    title="Distance"

                    value={`${emergency.transfer_distance_km} km`}
                />

                <Stat
                    title="ETA"

                    value={`${eta} mins`}
                />

            </div>

        </div>

    )

}

function Stat({

title,
value

}:{

title:string
value:string

}){

return(

<div className="rounded-lg border p-3">

<p className="text-xs text-slate-500">

{title}

</p>

<p className="font-semibold">

{value}

</p>

</div>

)

}