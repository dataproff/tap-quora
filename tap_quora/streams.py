"""Stream type classes for tap-quora."""

from __future__ import annotations
from singer_sdk import typing as th  # JSON Schema typing helpers
from tap_quora.client import QuoraStream
from typing import Optional, Iterable, Dict, Any
from datetime import date, timedelta


class BasicQuoraStream(QuoraStream):

    @property
    def start_date(self):
        # 28 is the maximum conversion window in Quora
        return self.config.get('start_date', date.today() - timedelta(days=28))

    @property
    def end_date(self):
        return self.config.get('end_date', date.today())


class AccountStream(BasicQuoraStream):

    @property
    def path(self):
        path = f"/accounts/{self.config.get('account_id')}"
        path = path + "?fields=accountId,campaignId"
        path = path + f"&startDate={self.start_date}"
        path = path + f"&endDate={self.end_date}"
        path = path + "&granularity=TOTAL"
        path = path + "&level=CAMPAIGN"
        return path

    """Define custom stream."""
    name = "account_stream"
    primary_keys = None
    replication_key = None
    schema = th.PropertiesList(
        th.Property("accountId", th.IntegerType),
        th.Property("campaignId", th.IntegerType),
        th.Property("startDate", th.DateType),
        th.Property("endDate", th.DateType),
    ).to_dict()

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """

        for campaign_row in self.request_records(context):
            campaign_row = self.post_process(campaign_row, context)
            campaign_row['startDate'] = f"{self.start_date}"
            campaign_row['endDate'] = f"{self.end_date}"
            yield campaign_row

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {
            "campaignId": record["campaignId"],
            "accountId": record["accountId"],
        }


class CampaignStream(BasicQuoraStream):
    parent_stream_type = AccountStream

    @property
    def path(self):
        path = "/campaigns/{campaignId}"
        path = path + "?fields=impressions,clicks,conversions,spend"
        path = path + f"&startDate={self.start_date}"
        path = path + f"&endDate={self.end_date}"
        path = path + "&granularity=DAY"
        path = path + "&level=CAMPAIGN"
        return path

    """Define custom stream."""
    name = "campaign_stream"
    primary_keys = None
    replication_key = None
    schema = th.PropertiesList(
        th.Property("accountId", th.IntegerType),
        th.Property("campaignId", th.IntegerType),
        th.Property("impressions", th.IntegerType),
        th.Property("clicks", th.IntegerType),
        th.Property("conversions", th.IntegerType),
        th.Property("spend", th.IntegerType),
        th.Property("startDate", th.DateType),
        th.Property("endDate", th.DateType),
    ).to_dict()

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        for day_row in self.request_records(context):
            day_row = self.post_process(day_row, context)
            day_row["conversions"] = day_row["conversions"]["Generic"]
            day_row["campaignId"] = context["campaignId"]
            day_row["accountId"] = context["accountId"]
            yield day_row
