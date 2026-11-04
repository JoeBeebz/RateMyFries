# FRY-57: verified local restaurant content

Story: https://ratemyfries.atlassian.net/browse/FRY-57

The class directory had five Google place IDs and no fry options. The curated manifest enriches four of those listings and adds ten Kenosha/Pleasant Prairie restaurants, yielding 37 fry options across 14 restaurants with photos. There are 20 dish-specific photos and 14 restaurant/brand photos (29 distinct image URLs). The existing Tr3s Hermanos listing and user-created placeholder remain intact.

## Sources and editorial choices

All menu descriptions are concise paraphrases of the restaurants' published menus. Full source URLs, photo context and the 2026-11-03 verification date remain in the manifest for maintainers. Following the user's class-project presentation request, visible descriptions contain only the restaurant or fry description. AJ's menu was read from both menu images on its official website, including its September 2026 effective date. Rivals' current two-page menu images were also inspected directly. Captain Mike's and MelKat's sources are their own Toast ordering sites. Chain menus are brand menus paired with independently verified local restaurant pages; availability should be confirmed with the restaurant.

No prices, ratings or reviews are added. A named spice blend or added toppings are classified as seasoned; plain/salted fries are classified as unseasoned under the existing boolean model. Unknown cuts use `other`. These categories do not provide ingredient/allergen guarantees.

Photos remain on the restaurant/brand's original HTTPS publishing hosts. Credits and photo context remain in the source manifest, outside the visitor-facing descriptions. Chain images represent the brand's food rather than the specific building; The Spot uses its official photographic menu banner. Restaurant food photos are not reused as a specific fry product unless the source identifies that item. No Google photo reference, image URL, coordinate or business-detail response is persisted. Google place IDs are retained and the existing application retrieves Google business details live.

Tr3s Hermanos had no accessible reliable menu/restaurant-owned photo source. Third-party reviews mentioning dishes were insufficient evidence for a curated menu. Its listing is preserved without speculative products or another restaurant's photo. The original owned placeholder has no verified business identity and is untouched.

## Operator procedure

1. Run the test suite and review the manifest. Check source/menu changes and that image URLs still serve the expected images. External links can change or disappear.
2. Run the importer against an isolated SQLite backup. Run it twice and confirm the second run adds nothing; inspect listing and fry pages before touching live content.
3. Schedule a brief service stop for the live write, so the backup and content operation share a quiet window. Run `tools/import_catalogue.py --database ABSOLUTE_DB_PATH --apply --backup-dir PRIVATE_BACKUP_DIRECTORY`. The backup contains account data; keep it outside the web root with restrictive filesystem permissions.
4. Restart the same application release, check database integrity/foreign keys and counts, and confirm the original user/review records and placeholder remain unchanged. Repeating the import must produce only `products_existing`.

The utility is an operator content tool, not a request handler, migration or startup seed. It has no network calls or credentials. Updates fill blank metadata; existing product names are skipped to preserve human edits and review IDs. It will not remove or reset existing data. A future menu revision needs deliberate editorial review instead of silently overwriting an existing product.

## Validation

54 Python checks pass, including six catalogue cases covering preview rollback, consistent backup, repeat import, review/edit preservation, owned-listing conflict rollback, duplicate identities and restricted/uncredited photo URLs. All 29 distinct image URLs returned image content. An isolated copy of the live database adds exactly ten restaurants and 37 products, enriches four original listings, and adds nothing on a repeat run. Teammate review/approval and merge remain required for the utility/manifest PR; Jira stays In Review until that workflow and acceptance checks are complete.

Live content acceptance on 2026-11-03: restaurant count increased from 6 to 16; fry count increased from 0 to 37. The original account, reviews, business requests and owned placeholder were compared before/after and stayed unchanged. Consistent backups were saved in the server's private `school/backups/FRY-57-catalogue/` directory before the import and before shortening source labels. Database integrity/foreign keys and repeat-import checks passed. The systemd service restarted successfully on the same application release, with source hashes unchanged. Live restaurant/menu photos rendered correctly on desktop. A captured live page rendered at 390 px confirmed that the shortened source labels fit the narrow layout; this was a content/CSS check, not a physical-device location-permission test. No runtime source change was deployed.

Presentation follow-up: catalogue descriptions now display only the restaurant/dish description. Source and verification metadata remain in the manifest, and no additional Jira story was created for this user-requested content cleanup.
