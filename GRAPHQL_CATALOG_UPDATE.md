# 24XSTORE — PlayStation GraphQL catalogue update

This update replaces the non-working HTML game-card scraper with the public PlayStation Store GraphQL catalogue request used by the storefront.

## What changed

- PS5 catalogue: Turkey storefront category `4cbf39e2-5749-4970-ba81-93a489e4570c`
- PS4 catalogue: Turkey storefront category `44d8bb20-653e-431e-8ad0-c0a365f68d2f`
- Store locale header: `tr-tr`
- Only `FULL_GAME` products are imported (DLC, add-ons and wallet/currency products are excluded)
- PS4/PS5 cross-gen platform detection
- cover, current TRY price, old TRY price and discount are stored
- GraphQL failures now produce a clear error instead of silently returning `found: 0`
- query hash can be overridden with `PS_STORE_QUERY_HASH`

## First test

After rebuild, run only two pages per platform first:

```bash
curl -X POST \
  -H "X-Admin-Token: 24xstore_sync_2026" \
  "http://localhost/api/catalog-sync?max_pages=2"
```

A successful response should have `games.source = "playstation_graphql"` and `games.found > 0`.

## If Sony changes the persisted query

Set a new value in the container environment:

```text
PS_STORE_QUERY_HASH=<current categoryGridRetrieve sha256Hash>
```

The code itself does not need to be edited.
