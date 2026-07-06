import { Badge } from "../../../components/ui/Badge"

interface Props {
    activeCount: number
}

export function EmergencyBanner({ activeCount }: Props) {

    return (

        <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-5 flex items-center justify-between">

            <div>

                <h2 className="text-xl font-bold text-red-700">
                    Emergency Operations Center
                </h2>

                <p className="text-sm text-red-600 mt-1">
                    AI Redistribution Engine • Real-Time Emergency Monitoring
                </p>

            </div>

            <div className="flex items-center gap-3">

                <Badge variant="red" pulse>
                    LIVE
                </Badge>

                <div className="text-right">

                    <p className="text-sm text-gray-500">
                        Active Emergencies
                    </p>

                    <p className="text-2xl font-bold text-red-700">

                        {activeCount}

                    </p>

                </div>

            </div>

        </div>

    )

}