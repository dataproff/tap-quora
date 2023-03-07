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

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        row['startDate'] = f"{self.start_date}"
        row['endDate'] = f"{self.end_date}"
        return row

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
        path = path + "?fields=campaignName,impressions,clicks,conversions,spend"
        path = path + "&conversionTypes=Generic,AppInstall,Purchase,GenerateLead,CompleteRegistration,AddPaymentInfo," \
                      "AddToCart,AddToWishlist,InitiateCheckout,Search"
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
        th.Property("campaignName", th.StringType),
        th.Property("impressions", th.IntegerType),
        th.Property("clicks", th.IntegerType),
        th.Property("conversions", th.ObjectType(
            th.Property("Generic", th.IntegerType),
            th.Property("AppInstall", th.IntegerType),
            th.Property("Purchase", th.IntegerType),
            th.Property("GenerateLead", th.IntegerType),
            th.Property("CompleteRegistration", th.IntegerType),
            th.Property("AddPaymentInfo", th.IntegerType),
            th.Property("AddToCart", th.IntegerType),
            th.Property("AddToWishlist", th.IntegerType),
            th.Property("InitiateCheckout", th.IntegerType),
            th.Property("Search", th.IntegerType),
        )),
        th.Property("spend", th.IntegerType),
        th.Property("startDate", th.DateType),
        th.Property("endDate", th.DateType),
    ).to_dict()
