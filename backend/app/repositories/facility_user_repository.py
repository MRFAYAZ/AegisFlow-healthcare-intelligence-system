from sqlalchemy import select

from app.models.facility_user import (
    FacilityUser
)

from app.repositories.base_repository import (
    BaseRepository
)


class FacilityUserRepository(
    BaseRepository
):

    def get_all(self):

        return (
            self.db.execute(
                select(FacilityUser)
            )
            .scalars()
            .all()
        )

    def get_by_facility(
        self,
        facility_id
    ):

        return (
            self.db.execute(
                select(FacilityUser)
                .where(
                    FacilityUser.facility_id
                    ==
                    facility_id
                )
            )
            .scalars()
            .all()
        )

    def get_by_user(
        self,
        user_id
    ):

        return (
            self.db.execute(
                select(FacilityUser)
                .where(
                    FacilityUser.user_id
                    ==
                    user_id
                )
            )
            .scalars()
            .all()
        )