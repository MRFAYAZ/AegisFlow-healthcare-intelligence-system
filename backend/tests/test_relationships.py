from app.core.database import SessionLocal

from app.models.facility import Facility
from app.models.inventory import InventoryCurrent
from app.models.alert import AlertEvent
from app.models.emergency import (
    EmergencyCase,
    EmergencySourceMatch
)
from app.models.redistribution import TransferRequest


def test_relationships():

    db = SessionLocal()

    try:

        print("\n" + "=" * 60)
        print("RELATIONSHIP VALIDATION")
        print("=" * 60)

        # ==================================================
        # FACILITY -> INVENTORY
        # ==================================================

        facility = (
            db.query(Facility)
            .first()
        )

        if facility:

            print("\n[Facility]")

            print(
                f"Facility: "
                f"{facility.facility_name}"
            )

            print(
                f"Inventories Found: "
                f"{len(facility.inventories)}"
            )

            print(
                "✅ Facility -> Inventory"
            )

        # ==================================================
        # INVENTORY -> MEDICINE
        # ==================================================

        inventory = (
            db.query(InventoryCurrent)
            .first()
        )

        if inventory:

            print("\n[Inventory]")

            print(
                f"Inventory ID: "
                f"{inventory.inventory_id}"
            )

            if inventory.medicine:

                print(
                    f"Medicine: "
                    f"{inventory.medicine.medicine_name}"
                )

                print(
                    "✅ Inventory -> Medicine"
                )

            if inventory.facility:

                print(
                    f"Facility: "
                    f"{inventory.facility.facility_name}"
                )

                print(
                    "✅ Inventory -> Facility"
                )

            print(
                f"Batches: "
                f"{len(inventory.batches)}"
            )

            print(
                "✅ Inventory -> Batches"
            )

        # ==================================================
        # ALERT -> FACILITY
        # ==================================================

        alert = (
            db.query(AlertEvent)
            .first()
        )

        if alert:

            print("\n[Alert]")

            print(
                f"Alert Type: "
                f"{alert.alert_type}"
            )

            if alert.facility:

                print(
                    f"Facility: "
                    f"{alert.facility.facility_name}"
                )

            print(
                "✅ Alert -> Facility"
            )

        else:

            print(
                "\n⚠ No alert records found"
            )

        # ==================================================
        # EMERGENCY -> FACILITY
        # ==================================================

        emergency = (
            db.query(EmergencyCase)
            .first()
        )

        if emergency:

            print("\n[Emergency]")

            print(
                f"Emergency ID: "
                f"{emergency.emergency_case_id}"
            )

            if emergency.facility:

                print(
                    f"Facility: "
                    f"{emergency.facility.facility_name}"
                )

            if emergency.medicine:

                print(
                    f"Medicine: "
                    f"{emergency.medicine.medicine_name}"
                )

            print(
                "✅ Emergency Relationships"
            )

        else:

            print(
                "\n⚠ No emergency records found"
            )

        # ==================================================
        # MATCH -> EMERGENCY
        # ==================================================

        match = (
            db.query(EmergencySourceMatch)
            .first()
        )

        if match:

            print("\n[Emergency Match]")

            print(
                f"Match ID: "
                f"{match.match_id}"
            )

            if match.emergency_case:

                print(
                    "Emergency Link Found"
                )

            if match.source_facility:

                print(
                    f"Source Facility: "
                    f"{match.source_facility.facility_name}"
                )

            print(
                "✅ Match Relationships"
            )

        else:

            print(
                "\n⚠ No emergency matches found"
            )

        # ==================================================
        # TRANSFER -> MEDICINE
        # ==================================================

        transfer = (
            db.query(TransferRequest)
            .first()
        )

        if transfer:

            print("\n[Transfer]")

            print(
                f"Transfer ID: "
                f"{transfer.transfer_id}"
            )

            if transfer.source_facility:

                print(
                    f"Source: "
                    f"{transfer.source_facility.facility_name}"
                )

            if transfer.destination_facility:

                print(
                    f"Destination: "
                    f"{transfer.destination_facility.facility_name}"
                )

            if transfer.medicine:

                print(
                    f"Medicine: "
                    f"{transfer.medicine.medicine_name}"
                )

            print(
                "✅ Transfer Relationships"
            )

        else:

            print(
                "\n⚠ No transfer records found"
            )

        print("\n" + "=" * 60)
        print("✅ RELATIONSHIP VALIDATION COMPLETE")
        print("=" * 60)

    except Exception as e:

        print(
            f"\n❌ Relationship Test Failed:\n{e}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":

    test_relationships()