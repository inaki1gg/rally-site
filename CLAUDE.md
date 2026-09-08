# rally-site

This is the actual marketing site — rallyrating.app. Plain HTML, no framework, no build step. Ownership moved here from Iñaki on 25 August 2026; check with Sascha whether every step in that handoff (`~/Desktop/RALLY_Website_Handoff_to_Sascha_2026-08-25.md`) is actually finished before assuming the live setup matches what's below.

## Two pages must never move

`/en/privacy` and `/en/support` are the exact addresses Apple has on file for this app. If either one moves, gets folded into another page, or stops loading, the app is at risk at the next Apple review. Never touch their address. Same for `/auth/reset-password` — that address is baked into app versions already on people's phones, including ones that can't be updated by pushing new code.

Any other page that's ever been public gets forwarded to its new address, never just deleted.

## The database is shared

This site's apply form and the app itself write to the same database. The same two rules apply here as everywhere else: never touch a rating, and never run a database change yourself — write it out and hand it to Sascha.

## Copy rules specific to this site

- Never describe the pairing or the draw as AI, machine learning, or smart. It's a straightforward sort. Say Elo, not intelligence.
- Never write copy that implies someone can appeal or correct a rating.
- The "for clubs" pitch can talk about seeding and standings. It cannot talk about booking courts, payments, or scheduling — that's not something Rally does yet.

## As of the handoff, two things were still open — confirm with Sascha before assuming either is fixed

- Whether pushes from Sascha's own account actually go live yet, or whether the site still only deploys from Iñaki's old commits.
- The Spanish privacy page was out of date against the English one, and the sign-up form's consent checkbox linked to that outdated page.
