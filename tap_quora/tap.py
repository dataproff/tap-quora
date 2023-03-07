"""quora tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_quora import streams


class Tapquora(Tap):
    """quora tap class."""

    name = "tap-quora"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The client id"
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,
            description="THe client secret"
        ),
        th.Property(
            "account_id",
            th.StringType,
            required=True,
            description="The account id",
        ),
        th.Property(
            "start_date",
            th.DateType,
            required=False,
            description="The date to start pulling data from",
        ),
        th.Property(
            "end_date",
            th.DateType,
            required=False,
            description="The date to stop pulling data from",
        ),
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            secret=True,
            description="The access token",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=True,
            secret=True,
            description="The refresh token",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.AccountStream, streams.CampaignStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.AccountStream(self),
            streams.CampaignStream(self),
        ]


if __name__ == "__main__":
    Tapquora.cli()
