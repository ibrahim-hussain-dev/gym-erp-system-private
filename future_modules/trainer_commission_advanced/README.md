# Trainer Commission — Advanced (automatic, per-invoice) module

**Status: NOT currently active on either VPS (production) or local (dev).**
This is the full, automated version of trainer commission tracking that was
built and tested, then intentionally disabled on production because the
client did not want it at the time (2026-10). It is preserved here, complete
and ready to re-apply, for whenever the client asks for it in future.

## What this does

Every time a Sales Invoice is submitted, for each line item that maps to a
Gym Plan with an assigned Trainer, it:

1. Calculates a one-time commission = line amount x trainer's commission %.
2. Inserts a `Gym Trainer Commission` record (full audit log: trainer, invoice,
   member, plan, sale amount, commission %, commission amount, date).
3. Adds that amount to the trainer's running `total_commission_earned`.

This is the automatic, continuously-logging version. Both VPS and local
currently run the simpler version instead: the `commission_percentage` and
`total_commission_earned` fields still exist on Gym Trainer (and the "Gym
Trainer Commission" ranking report still works off those two fields), but
nothing updates `total_commission_earned` automatically — it has to be
entered/updated manually, and no per-invoice log is kept.

## Files in this folder

- `trainer_commission.py` — the hook function (`log_commission_from_invoice`).
  Goes at: `gym_management/gym_management/gym_erp_system/trainer_commission.py`
- `doctype/gym_trainer_commission/` — the full `Gym Trainer Commission` DocType
  (the per-invoice audit log table): `.json` schema, `.py` controller, `.js`
  client stub, `__init__.py`, and its integration test file.
  Goes at: `gym_management/gym_management/gym_erp_system/doctype/gym_trainer_commission/`

Note: the "Gym Trainer Commission" **report** (the ranking/summary report
shown as a shortcut on the workspace) is NOT included here — it already
exists, identically, on both VPS and local, and does not depend on anything
in this folder (it reads straight from the `commission_percentage` /
`total_commission_earned` fields on Gym Trainer). It is unaffected either way.

## How to re-apply this in future (if the client asks for it)

Do this on a quiet/maintenance window, same careful pattern as every other
change to this app — back up first, verify, never guess.

1. **Back up first.** On the target environment (VPS or local), back up the
   current `gym_management` app folder (timestamped tar/zip) before touching
   anything.

2. **Copy the files in**, matching the paths above:
   - `trainer_commission.py` → `.../gym_erp_system/trainer_commission.py`
   - the whole `doctype/gym_trainer_commission/` folder →
     `.../gym_erp_system/doctype/gym_trainer_commission/`

3. **Wire up the hook in `hooks.py`.** Find the `doc_events` dict's
   `"Sales Invoice"` → `"on_submit"` entry. If it's currently a single string
   (not a list), turn it into a list and add this module's function:

   ```python
   "on_submit": [
       "gym_management.gym_erp_system.gym_subscription.create_subscription_from_invoice",
       "gym_management.gym_erp_system.trainer_commission.log_commission_from_invoice"
   ],
   ```

4. **Sync just this one DocType into the database — do NOT run `bench migrate`.**
   A full `bench migrate` is what deleted the Front Desk / Owner workspaces on
   2026-10-21 (its orphan-doctype/entity cleanup step runs right after fixture
   sync, in the same run, and is not prevented by fixture protection). Use the
   targeted, single-doctype sync instead, which does not run that cleanup step:

   ```bash
   docker exec -u frappe -w /home/frappe/frappe-bench <backend-container> \
     bench --site <site-name> reload-doctype "Gym Trainer Commission"
   ```

5. **Add fixture coverage** (optional but recommended) so this DocType's
   permissions survive future fixture exports — add an entry to the
   `Custom DocPerm` fixture filter list in `hooks.py`, or add a dedicated
   `Role`/`Custom DocPerm` fixture entry if a new role should access it.

6. **Restart the app containers** (`docker restart <containers>` — never
   `bench migrate`), then health-check the site, then test: submit a test
   Sales Invoice for a member on a plan with an assigned, commission-earning
   trainer, and confirm a `Gym Trainer Commission` record appears and the
   trainer's `total_commission_earned` increases.

## Known related issue on VPS (as of 2026-10-21, not yet fixed)

When this module was removed from VPS, the `Gym Trainer Commission` DocType's
JSON schema file was deleted from the app code, but its database table and
DocType metadata record were left behind (confirmed via
`frappe.db.exists("DocType", "Gym Trainer Commission")` returning true on
VPS, while no matching `.json` file exists in the VPS app folder — only an
orphaned `.py` controller file remains). This is a dormant, "orphaned"
DocType: it is not wired into any hook and nothing in the UI creates records
in it anymore, but because its JSON is missing from the app folder, it is
exactly the kind of record `bench migrate`'s orphan-doctype-removal step
deletes — the same mechanism that deleted the Workspaces. If `bench migrate`
is ever run on VPS again, this DocType (and its table, if it has any data)
would likely be silently removed. This should be cleaned up deliberately
(either restore the `.json` to make it complete and intentionally re-enable
it, or safely drop the orphaned table/DocType record directly) rather than
left to be silently deleted by a future `migrate`. Not yet actioned — flagged
here for follow-up.
