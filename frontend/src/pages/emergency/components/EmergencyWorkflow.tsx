import type { Emergency } from "../../../types/emergency"

interface Props {
    emergency: Emergency
}

const workflow = [
    "ACTIVE",
    "MATCHING",
    "PENDING",
    "APPROVED",
    "IN_TRANSIT",
    "COMPLETED",
    "RESOLVED"
]

const labels = {
    ACTIVE: "Emergency Raised",
    MATCHING: "Source Matching",
    PENDING: "Awaiting Donor Approval",
    APPROVED: "Dispatcher Assigned",
    IN_TRANSIT: "Medicine In Transit",
    COMPLETED: "Delivered",
    RESOLVED: "Closed",
}

export function EmergencyWorkflow({ emergency }: Props) {

    let current = 0

    if (emergency.transfer_status === "PENDING")
        current = 2

    else if (emergency.transfer_status === "APPROVED")
        current = 3

    else if (emergency.transfer_status === "IN_TRANSIT")
        current = 4

    else if (emergency.transfer_status === "COMPLETED")
        current = 5

    if (emergency.emergency_status === "RESOLVED")
        current = 6

    return (

        <div className="rounded-xl border bg-white p-5">

            <h3 className="font-semibold text-lg mb-5">
                Emergency Workflow
            </h3>

            <div className="space-y-4">

                {workflow.map((step, index) => {

                    const completed = index < current

                    const active = index === current

                    return (

                        <div
                            key={step}
                            className="flex items-start gap-3"
                        >

                            <div
                                className={`
                                h-5
                                w-5
                                rounded-full
                                mt-0.5

                                ${
                                    completed
                                    ? "bg-green-500"

                                    : active

                                    ? "bg-blue-600"

                                    : "bg-slate-300"
                                }
                                `}
                            />

                            <div>

                                <p className="font-medium">

                                    {labels[
                                        step as keyof typeof labels
                                    ]}

                                </p>

                                <p className="text-xs text-slate-500">

                                    {
                                        completed

                                        ? "Completed"

                                        : active

                                        ? "Current Step"

                                        : "Pending"
                                    }

                                </p>

                            </div>

                        </div>

                    )

                })}

            </div>

        </div>

    )

}