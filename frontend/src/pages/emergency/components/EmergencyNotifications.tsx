import type { Emergency } from "../../../types/emergency"

interface Props{
    emergencies: Emergency[]
}

export function EmergencyNotifications({

    emergencies

}:Props){

    const notifications = emergencies
        .slice(0,6)
        .map((e)=>{

            let title=""

            let color="bg-blue-500"

            if(e.transfer_status==="PENDING"){

                title="Waiting for donor approval"
                color="bg-yellow-500"

            }

            else if(e.transfer_status==="APPROVED"){

                title="Hospital approved transfer"
                color="bg-green-500"

            }

            else if(e.transfer_status==="IN_TRANSIT"){

                title="Vehicle dispatched"
                color="bg-blue-600"

            }

            else if(e.transfer_status==="COMPLETED"){

                title="Medicine delivered"
                color="bg-green-600"

            }

            else{

                title="AI donor matching started"

            }

            return{

                id:e.emergency_case_id,

                medicine:e.medicine_name,

                facility:e.facility_name,

                title,

                color

            }

        })

    return(

        <div className="operations-feed panel">

            <div className="flex items-center justify-between mb-4">

                <h3 className="font-semibold text-lg">

                    Live Notifications

                </h3>

                <span className="text-xs text-slate-500">

                    Live stream

                </span>

            </div>

            <div className="space-y-3">

                {notifications.map((n)=>(

                    <div
                        key={n.id}
                        className="operation-event"
                    >

                        <div
                            className={`w-3 h-3 rounded-full mt-1 ${n.color}`}
                        />

                        <div>

                            <p className="font-medium">

                                {n.title}

                            </p>

                            <p className="text-sm text-ink-muted">

                                {n.medicine}

                            </p>

                            <p className="text-xs text-ink-faint">

                                {n.facility}

                            </p>

                        </div>

                    </div>

                ))}

            </div>

        </div>

    )

}