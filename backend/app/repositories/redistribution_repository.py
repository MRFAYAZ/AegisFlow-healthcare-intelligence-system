from uuid import UUID

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import (
    Session,
    aliased,
)

from app.models.facility import Facility
from app.models.inventory import InventoryCurrent
from app.models.medicine import Medicine
from app.models.dispatch import TransferDispatch

from app.models.redistribution import (
    TransferRequest,
)

from app.core.enums import (
    TransferStatusEnum,
)

from app.repositories.base_repository import (
    BaseRepository,
)


class RedistributionRepository(
    BaseRepository
):

    def __init__(
        self,
        db: Session,
    ):

        super().__init__(db)

    def get_dispatch_queue(self):
        SourceFacility = aliased(Facility)
        DestinationFacility = aliased(Facility)

        query = (
            select(
                TransferRequest.transfer_id,
                TransferRequest.emergency_case_id,
                TransferRequest.from_facility_id,
                SourceFacility.facility_name.label("from_facility_name"),
                TransferRequest.to_facility_id,
                DestinationFacility.facility_name.label("to_facility_name"),
                Medicine.medicine_name,
                TransferRequest.approved_quantity,
                TransferRequest.transfer_status,
                TransferRequest.transfer_distance_km,
                TransferDispatch.dispatch_id,
                TransferDispatch.transport_type,
                TransferDispatch.vehicle_reference,
                TransferDispatch.status.label("dispatch_status"),
                TransferDispatch.dispatched_at,
                TransferDispatch.delivered_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id == Medicine.medicine_id,
            )
            .outerjoin(
                TransferDispatch,
                TransferRequest.transfer_id == TransferDispatch.transfer_id,
            )
            .where(
                TransferRequest.transfer_status.in_(
                    [TransferStatusEnum.APPROVED, TransferStatusEnum.IN_TRANSIT]
                )
            )
            .order_by(TransferRequest.transfer_distance_km.asc())
        )

        return self.db.execute(query).mappings().all()

    def get_delivered_today_count(self) -> int:
        start_of_day = datetime.now(timezone.utc).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        query = select(func.count(TransferDispatch.dispatch_id)).where(
            TransferDispatch.delivered_at >= start_of_day
        )
        return int(self.db.execute(query).scalar_one())

    # =====================================================
    # GET PENDING TRANSFERS
    # =====================================================

    def get_pending_transfers(
        self,
    ):

        query = (
            select(TransferRequest)
            .where(
                TransferRequest.transfer_status
                == TransferStatusEnum.PENDING
            )
            .order_by(
                TransferRequest.requested_at.asc()
            )
        )

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )

    # =====================================================
    # GET TRANSFER BY ID
    #
    # Returns the raw TransferRequest ORM object.
    #
    # Used when the service needs to work directly with
    # the transfer entity.
    # =====================================================

    def get_transfer_by_id(
        self,
        transfer_id: UUID,
    ):

        query = (
            select(TransferRequest)
            .where(
                TransferRequest.transfer_id
                == transfer_id
            )
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET TRANSFER RESPONSE BY ID
    #
    # Returns the enriched transfer projection required
    # by TransferResponse.
    #
    # Unlike get_transfer_by_id(), this method joins:
    #
    #   TransferRequest
    #       ↓
    #   Source Facility
    #       ↓
    #   Destination Facility
    #       ↓
    #   Medicine
    #
    # This provides:
    #
    #   from_facility_name
    #   to_facility_name
    #   medicine_name
    #
    # This is especially important after approval because
    # approve_transfer() performs its transaction using
    # the raw ORM entity but the API response requires the
    # enriched representation.
    # =====================================================

    def get_transfer_response_by_id(
        self,
        transfer_id: UUID,
    ):

        SourceFacility = aliased(
            Facility
        )

        DestinationFacility = aliased(
            Facility
        )

        query = (
            select(
                TransferRequest.transfer_id,

                TransferRequest.emergency_case_id,

                TransferRequest.from_facility_id,

                SourceFacility.facility_name.label(
                    "from_facility_name"
                ),

                TransferRequest.to_facility_id,

                DestinationFacility.facility_name.label(
                    "to_facility_name"
                ),

                TransferRequest.medicine_id,

                Medicine.medicine_name,

                TransferRequest.requested_quantity,

                TransferRequest.approved_quantity,

                TransferRequest.transfer_status,

                TransferRequest.cascade_safe,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.recommendation_reason,

                TransferRequest.requested_by,

                TransferRequest.approved_by,

                TransferRequest.approved_at,

                TransferRequest.requested_at,

                TransferRequest.completed_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id
                == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id
                == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id
                == Medicine.medicine_id,
            )
            .where(
                TransferRequest.transfer_id
                == transfer_id
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .one_or_none()
        )

    # =====================================================
    # GET TRANSFER FOR APPROVAL
    #
    # Locks the transfer row so that concurrent approval
    # requests cannot modify the same transfer at the
    # same time.
    # =====================================================

    def get_transfer_for_approval(
        self,
        transfer_id: UUID,
    ):

        query = (
            select(TransferRequest)
            .where(
                TransferRequest.transfer_id
                == transfer_id
            )
            .with_for_update()
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET INVENTORY FOR TRANSFER
    #
    # Locks the donor inventory row.
    #
    # This is critical during approval because two
    # simultaneous emergency approvals must not both
    # consume the same available stock.
    # =====================================================

    def get_inventory_for_transfer(
        self,
        facility_id: UUID,
        medicine_id: UUID,
    ):

        query = (
            select(InventoryCurrent)
            .where(
                InventoryCurrent.facility_id
                == facility_id,

                InventoryCurrent.medicine_id
                == medicine_id,
            )
            .with_for_update()
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET TRANSFERS FOR FACILITY
    # =====================================================

    def get_transfers_for_facility(
        self,
        facility_id: UUID,
    ):

        SourceFacility = aliased(
            Facility
        )

        DestinationFacility = aliased(
            Facility
        )

        query = (
            select(
                TransferRequest.transfer_id,

                TransferRequest.emergency_case_id,

                TransferRequest.from_facility_id,

                SourceFacility.facility_name.label(
                    "from_facility_name"
                ),

                TransferRequest.to_facility_id,

                DestinationFacility.facility_name.label(
                    "to_facility_name"
                ),

                TransferRequest.medicine_id,

                Medicine.medicine_name,

                TransferRequest.requested_quantity,

                TransferRequest.approved_quantity,

                TransferRequest.transfer_status,

                TransferRequest.cascade_safe,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.recommendation_reason,

                TransferRequest.requested_by,

                TransferRequest.approved_by,

                TransferRequest.approved_at,

                TransferRequest.requested_at,

                TransferRequest.completed_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id
                == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id
                == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id
                == Medicine.medicine_id,
            )
            .where(
                (
                    TransferRequest.from_facility_id
                    == facility_id
                )
                |
                (
                    TransferRequest.to_facility_id
                    == facility_id
                )
            )
            .order_by(
                TransferRequest.requested_at.desc()
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

    # =====================================================
    # CREATE TRANSFER REQUEST
    #
    # Repository does NOT commit.
    #
    # The service owns the transaction boundary.
    # =====================================================

    def create_transfer_request(
        self,
        transfer_data: dict,
    ):

        transfer = TransferRequest(
            **transfer_data
        )

        self.db.add(
            transfer
        )

        self.db.flush()

        return transfer

    # =====================================================
    # GET ALL TRANSFERS
    # =====================================================

    def get_all_transfers(
        self,
    ):

        SourceFacility = aliased(
            Facility
        )

        DestinationFacility = aliased(
            Facility
        )

        query = (
            select(
                TransferRequest.transfer_id,

                TransferRequest.emergency_case_id,

                TransferRequest.from_facility_id,

                SourceFacility.facility_name.label(
                    "from_facility_name"
                ),

                TransferRequest.to_facility_id,

                DestinationFacility.facility_name.label(
                    "to_facility_name"
                ),

                TransferRequest.medicine_id,

                Medicine.medicine_name,

                TransferRequest.requested_quantity,

                TransferRequest.approved_quantity,

                TransferRequest.transfer_status,

                TransferRequest.cascade_safe,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.recommendation_reason,

                TransferRequest.requested_by,

                TransferRequest.approved_by,

                TransferRequest.approved_at,

                TransferRequest.requested_at,

                TransferRequest.completed_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id
                == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id
                == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id
                == Medicine.medicine_id,
            )
            .order_by(
                TransferRequest.requested_at.desc()
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

    # =====================================================
    # GET HIGH PRIORITY TRANSFERS
    # =====================================================

    def get_high_priority_transfers(
        self,
    ):

        SourceFacility = aliased(
            Facility
        )

        DestinationFacility = aliased(
            Facility
        )

        query = (
            select(
                TransferRequest.transfer_id,

                TransferRequest.emergency_case_id,

                TransferRequest.from_facility_id,

                SourceFacility.facility_name.label(
                    "from_facility_name"
                ),

                TransferRequest.to_facility_id,

                DestinationFacility.facility_name.label(
                    "to_facility_name"
                ),

                TransferRequest.medicine_id,

                Medicine.medicine_name,

                TransferRequest.requested_quantity,

                TransferRequest.approved_quantity,

                TransferRequest.transfer_status,

                TransferRequest.cascade_safe,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.recommendation_reason,

                TransferRequest.requested_by,

                TransferRequest.approved_by,

                TransferRequest.approved_at,

                TransferRequest.requested_at,

                TransferRequest.completed_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id
                == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id
                == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id
                == Medicine.medicine_id,
            )
            .where(
                TransferRequest.match_score >= 80
            )
            .order_by(
                TransferRequest.match_score.desc(),

                TransferRequest.requested_at.asc(),
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

    # =====================================================
    # GET TRANSFERS BY STATUS
    # =====================================================

    def get_transfers_by_status(
        self,
        status: TransferStatusEnum,
    ):

        SourceFacility = aliased(
            Facility
        )

        DestinationFacility = aliased(
            Facility
        )

        query = (
            select(
                TransferRequest.transfer_id,

                TransferRequest.emergency_case_id,

                TransferRequest.from_facility_id,

                SourceFacility.facility_name.label(
                    "from_facility_name"
                ),

                TransferRequest.to_facility_id,

                DestinationFacility.facility_name.label(
                    "to_facility_name"
                ),

                TransferRequest.medicine_id,

                Medicine.medicine_name,

                TransferRequest.requested_quantity,

                TransferRequest.approved_quantity,

                TransferRequest.transfer_status,

                TransferRequest.cascade_safe,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.recommendation_reason,

                TransferRequest.requested_by,

                TransferRequest.approved_by,

                TransferRequest.approved_at,

                TransferRequest.requested_at,

                TransferRequest.completed_at,
            )
            .join(
                SourceFacility,
                TransferRequest.from_facility_id
                == SourceFacility.facility_id,
            )
            .join(
                DestinationFacility,
                TransferRequest.to_facility_id
                == DestinationFacility.facility_id,
            )
            .join(
                Medicine,
                TransferRequest.medicine_id
                == Medicine.medicine_id,
            )
            .where(
                TransferRequest.transfer_status
                == status
            )
            .order_by(
                TransferRequest.requested_at.asc()
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

    # =====================================================
    # REDISTRIBUTION DASHBOARD
    # =====================================================

    def get_dashboard(
        self,
    ):

        transfers = (
            self.get_all_transfers()
        )

        high_priority = [
            transfer
            for transfer in transfers
            if (
                transfer["match_score"] is not None
                and float(
                    transfer["match_score"]
                ) >= 80
            )
        ]

        scored_transfers = [
            float(
                transfer["match_score"]
            )
            for transfer in transfers
            if transfer["match_score"] is not None
        ]

        average_match_score = 0.0

        if scored_transfers:

            average_match_score = (
                sum(scored_transfers)
                / len(scored_transfers)
            )

        return {
            "total_transfers": len(
                transfers
            ),

            "pending": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.PENDING
                    )
                ]
            ),

            "approved": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.APPROVED
                    )
                ]
            ),

            "rejected": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.REJECTED
                    )
                ]
            ),

            "in_transit": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.IN_TRANSIT
                    )
                ]
            ),

            "completed": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.COMPLETED
                    )
                ]
            ),

            "cancelled": len(
                [
                    transfer
                    for transfer in transfers
                    if (
                        transfer["transfer_status"]
                        == TransferStatusEnum.CANCELLED
                    )
                ]
            ),

            "high_priority": len(
                high_priority
            ),

            "average_match_score": round(
                average_match_score,
                2,
            ),
        }