from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.redistribution import (
    TransferRequest
)

from app.core.enums import (
    TransferStatusEnum
)

from app.repositories.base_repository import (
    BaseRepository
)


class RedistributionRepository(
    BaseRepository
):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # GET PENDING TRANSFERS
    # =====================================================

    def get_pending_transfers(self):

        query = (
            select(TransferRequest)
            .where(
                TransferRequest.transfer_status ==
                TransferStatusEnum.PENDING
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET TRANSFERS FOR FACILITY
    # =====================================================

    def get_transfers_for_facility(
        self,
        facility_id
    ):

        query = (
            select(TransferRequest)
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
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # CREATE TRANSFER REQUEST
    # =====================================================

    def create_transfer_request(
        self,
        transfer_data
    ):

        transfer = TransferRequest(
            **transfer_data
        )

        self.db.add(transfer)

        self.db.commit()

        self.db.refresh(transfer)

        return transfer
    
    # =====================================================
    # GET ALL TRANSFERS
    # =====================================================

    def get_all_transfers(self):

        query = select(TransferRequest)

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )


    # =====================================================
    # GET HIGH PRIORITY TRANSFERS
    # =====================================================

    def get_high_priority_transfers(self):

        query = (
            select(TransferRequest)
            .where(
                TransferRequest.match_score >= 80
            )
        )

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )


    # =====================================================
    # REDISTRIBUTION DASHBOARD
    # =====================================================

    def get_dashboard(self):

        transfers = self.get_all_transfers()

        high_priority = [
            t for t in transfers
            if t.match_score and t.match_score >= 80
        ]

        avg_score = 0

        scored_transfers = [
            float(t.match_score)
            for t in transfers
            if t.match_score is not None
        ]

        if scored_transfers:
            avg_score = (
                sum(scored_transfers)
                /
                len(scored_transfers)
            )

        return {

            "total_transfers":
                len(transfers),

            "pending":
                len(
                    [
                        t for t in transfers
                        if t.transfer_status
                        ==
                        TransferStatusEnum.PENDING
                    ]
                ),

            "approved":
                len(
                    [
                        t for t in transfers
                        if t.transfer_status
                        ==
                        TransferStatusEnum.APPROVED
                    ]
                ),

            "completed":
                len(
                    [
                        t for t in transfers
                        if t.transfer_status
                        ==
                        TransferStatusEnum.COMPLETED
                    ]
                ),

            "high_priority":
                len(high_priority),

            "average_match_score":
                round(avg_score, 2)
        }