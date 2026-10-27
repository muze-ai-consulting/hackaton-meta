# Meta Ad Library API (ads_archive): what it returns — verified 2026-10-27

Sources:
- ArchivedAd reference (official): https://developers.facebook.com/docs/graph-api/reference/archived-ad/
- ads_archive endpoint (official): https://developers.facebook.com/docs/graph-api/reference/ads_archive/
- Third-party guide, 2026-06-13: https://adlibrary.com/posts/eu-dsa-ad-repositories-developers
- Radlibrary changelog (facebookresearch): https://github.com/facebookresearch/Radlibrary/blob/HEAD/NEWS.md

## Fields available for ALL ads (incl. commercial)
id, ad_creation_time, ad_creative_bodies, ad_creative_link_captions, ad_creative_link_descriptions, ad_creative_link_titles,
ad_delivery_start_time, ad_delivery_stop_time ("The time when an advertiser wants to stop delivery of their ad"; blank = runs until stopped or budget spent — it is the PLANNED stop, not observed),
ad_snapshot_url (renders the archived ad with uncompressed images/video), languages, page_id, page_name, publisher_platforms.

## Fields only for ads delivered to the UK/EU (DSA Art. 39) — the commercial ground truth
- eu_total_reach: "The estimated combined ad reach for all locations inside the European Union." int32, EU ads only. One number per ad covering its whole run (third-party).
- total_reach_by_location (EU, BR, UK)
- age_country_gender_reach_breakdown (UK & EU)
- target_ages, target_gender, target_locations (UK & EU)
- beneficiary_payers (EU only)

## Political/issue ads only (NOT available for commercial ads)
spend, impressions, currency, demographic_distribution, estimated_audience_size, delivery_by_region, bylines.
=> For commercial ads there is NO spend and NO impressions. Reach (EU/UK) is the only performance signal.

## Scope / access
- "Ads that did not reach any location in the EU will only return if they are about social issues, elections or politics." => commercial backtest must use EU/UK-delivered ads (Chile/US commercial ads are not queryable).
- Access: identity + location confirmation at facebook.com/ID by the Facebook user behind the token (government ID), developer app, tokens ~60 days (third-party). This is a human step for Mark; takes time — do on day 0.
- Rate limit: error 613 documented; "200 calls/hour" figure only from a third-party teaser (unverified).
- Media: no media URL fields; no batch download; individual downloads of creative allowed "for analysis" subject to Meta's data storage terms. Use ad_snapshot_url per ad.
- Retention: each ad stays available 1 year after last impression (DSA Art. 39, third-party); repositories are rolling windows.
- Endpoint is read-only.

## Coordinator inferences (not sourced)
- Raw eu_total_reach is confounded by budget. Usable signal = WITHIN-ADVERTISER comparison: variants from the same page launched the same week; Meta's delivery (Advantage+) shifts budget toward better creatives, so reach share within a batch and longevity (still active vs stopped early) are proxies of performance.
- Contamination guard: only ads with ad_delivery_start_time after 2026-09-02 (Muse Spark 1.3 release).
- Live forward test: ads launched Oct 27–Nov 1 by tracked EU advertisers; hash-commit predicted ranking before Nov 4; resolve with eu_total_reach and active status re-queried during judging (Nov 4–8) and afterwards.
- Active status can be filtered with the ad_active_status request parameter (ACTIVE/INACTIVE/ALL) — confirm on day 0.
