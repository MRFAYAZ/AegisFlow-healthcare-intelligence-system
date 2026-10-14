import { Badge } from "../../../components/ui/Badge"
import { Activity, Radio } from "lucide-react"

interface Props {
    activeCount: number
}

export function EmergencyBanner({ activeCount }: Props) {

    return (

        <div className="emergency-banner-panel">

            <div>

                <div className="section-kicker danger-kicker"><Activity size={14} /> Priority response channel</div>
                <h2 className="text-xl font-bold text-ink">
                    Emergency response network
                </h2>

                <p className="text-sm text-ink-muted mt-1">
                    Live incident intake and explainable redistribution decisions
                </p>

            </div>

            <div className="flex items-center gap-3">

                <Badge variant="red" pulse>
                    <Radio size={13} /> LIVE
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