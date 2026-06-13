from app.repositories.facility_user_repository import (
    FacilityUserRepository
)


class FacilityUserService:

    def __init__(
        self,
        db
    ):

        self.repository = (
            FacilityUserRepository(db)
        )

    def get_all(self):

        return (
            self.repository
            .get_all()
        )

    def get_by_facility(
        self,
        facility_id
    ):

        return (
            self.repository
            .get_by_facility(
                facility_id
            )
        )

    def get_by_user(
        self,
        user_id
    ):

        return (
            self.repository
            .get_by_user(
                user_id
            )
        )