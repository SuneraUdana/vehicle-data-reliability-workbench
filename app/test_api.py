from app.api import ListingRequest, assess_listing


def test_known_comparable_listing_is_plausible() -> None:
    result = assess_listing(
        ListingRequest(
            brand="TOYOTA",
            model="VITZ",
            year_of_manufacture=2007,
            price=53.810526315789474,
        )
    )
    assert result.status == "appears_plausible"
    assert result.price_anomaly is False
    assert result.group_count >= 5


def test_unknown_comparable_group_is_explicitly_uncertain() -> None:
    result = assess_listing(
        ListingRequest(
            brand="NOT_IN_REFERENCE",
            model="UNKNOWN",
            year_of_manufacture=2020,
            price=50,
        )
    )
    assert result.status == "insufficient_evidence"
    assert result.price_anomaly is None
