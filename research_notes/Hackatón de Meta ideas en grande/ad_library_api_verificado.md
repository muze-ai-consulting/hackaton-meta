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

## Día 0 (27-oct-2026): términos y comportamiento, verificado en facebook.com/ads/library/api y developers.facebook.com/terms

- Cobertura: anuncios de cualquier tipo entregados en UK o la UE "durante el último año". Cubre todo lo posterior al 2-sep-2026.
- `ad_delivery_start_time` es observado: desde agosto de 2020 la fecha de inicio "se genera cuando un anuncio entrega una impresión por primera vez". La fecha de término sigue siendo dudosa para anuncios activos.
- Paginación: hasta 5.000 anuncios por página de resultados, seguir `paging.next`. `search_page_ids` acepta hasta 10 IDs por consulta. `search_terms` máximo 100 caracteres. `ad_reached_countries` es obligatorio. Versión vigente de la Graph API: v26.0.
- Creatividades: no hay descarga en lote; se puede descargar imagen y texto de un anuncio individual "para análisis", cumpliendo los términos de almacenamiento.
- Términos de la plataforma (§3.a.iv): prohibido vender, licenciar o comprar datos de la plataforma. §3.d.i.2: borrar los datos cuando ya no se necesiten o al dejar de operar el producto. §3.a.viii: solo usos permitidos por la documentación. El texto no menciona explícitamente el entrenamiento de modelos.
- Publicación: la FAQ permite "crear y publicar informes o artículos" y publicar los datos procesados o analizados. Los datos crudos solo se comparten con quien también tenga verificación en Facebook.com/ID y cuenta de desarrollador.
- **Consecuencias para Ensayo:**
  - Guardar las creatividades solo en `data/raw/` (ya está en `.gitignore`) y borrarlas después de la hackatón.
  - En el repo y en el demo publicar solo métricas agregadas y rankings, nunca el dataset crudo.
  - No usar los datos para ajustar modelos: Spark 1.3 no se ajusta, así que no aplica.
- La web de la Ad Library tiene un filtro de fechas por impresiones, no por fecha de inicio. Además, muchos anuncios muestran "Este anuncio tiene varias versiones" (creatividad dinámica): esas variantes comparten un solo ID y su alcance no se puede separar, así que el backtest compara IDs distintos.
- Anunciantes de catálogo (por ejemplo Zalando: anuncios por producto con el mismo texto) no sirven para comparar creatividades. Hay que filtrarlos.
