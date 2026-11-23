# PackTrack setup

Two pieces: one HTML page on your website, one Google Apps Script that
stores the data in a Google Sheet you own.

## Where the data goes

Every record a phone saves is appended as a row in a Google Sheet in your
Drive, in four tabs: `dogs`, `shakes`, `focals`, `gates`. Dog photos are
saved to a Drive folder named "PackTrack dog photos" (created for you), and
the sheet stores each photo's thumbnail URL. The Results tab of the web page
reads the same data back every ~10 seconds.

## One-time setup (about 5 minutes)

1. Go to sheets.google.com and create a blank spreadsheet. Name it
   "PackTrack data".
2. In the spreadsheet: Extensions -> Apps Script. Delete the starter code,
   paste in the contents of `code.gs`, and save.
3. In the Apps Script editor, select the function `setup` in the toolbar
   dropdown and click Run. Google asks you to authorize the script (it needs
   access to this sheet and to Drive for the photo folder). Approve it. The
   four tabs and the photo folder now exist.
4. Click Deploy -> New deployment -> type: Web app.
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click Deploy and copy the Web app URL (ends in `/exec`).
5. Open `packtrack.html` in a text editor. Near the top of the `<script>`
   block, replace `PASTE_YOUR_WEB_APP_URL_HERE` with that URL.
6. Upload `packtrack.html` to your website. Done. Open it on your phone,
   register a test dog, and confirm a row appears in the sheet.

## NC State logo

The header has an `<img class="logo">` slot. Download the official logo from
the NC State brand site, upload it next to the page, and set the img tag's
`src` to that file. The page looks fine without it.

## Changing the name

"PackTrack" appears in the page title, the header, and the Guide text. A
find-and-replace in `packtrack.html` renames it everywhere.

## Test it before class (about 10 minutes)

Do this on your phone, exactly as a student would.

1. **Check the endpoint is public.** Open your web app URL with `?mode=data` on
   the end in a **private / incognito window**. You should see raw JSON starting
   `{"ok":true`. A Google sign-in page means students will not be able to submit:
   fix it under Deploy -> Manage deployments -> pencil -> Who has access:
   **Anyone** (not "Anyone with Google account"). An error naming a missing
   sheet means `setup()` has not been run yet.
2. Open the page on your phone. The chip in the header should say "synced" with
   a time. "offline" means the page cannot reach the endpoint.
3. Set your observer name (tap the Observer chip).
4. **Dogs tab:** photograph something (your own dog, a friend's, a stuffed
   animal), add a name and the four descriptors, tap Add dog. Within about ten
   seconds a row should appear in the `dogs` tab of the sheet, and a JPEG in the
   "PackTrack dog photos" folder in your Drive.
5. **Open the page on a second device or browser.** The dog you just registered
   should appear in its registry grid with the photo. This is the test that
   matters most: it proves the shared-data path works in both directions.
6. **Shake tab:** log one shake. Check the row lands in the `shakes` tab.
7. **Focal tab:** tap a behavior, let the 10 s timer beep, tap the second
   behavior, save.
8. **Gate tab:** tap START, then SHOOK a few seconds later, and save.
9. **Results tab:** counts should match what you entered. Tap "Refresh data &
   stats".
10. **Offline test:** turn on airplane mode, save one more shake. The header
    should turn into a red "1 queued". Turn the connection back on; within
    fifteen seconds it should say "synced" and the row should appear.
11. **Delete test:** on a form, use the Delete button next to one of your recent
    entries and confirm the row disappears from the sheet.

## Clearing the test data before class

Two functions are in `code.gs`. Open the spreadsheet, go to Extensions -> Apps
Script, pick the function name in the toolbar dropdown, and click Run. Running a
function from the editor does **not** require redeploying, so the live page keeps
working while you do this.

- **`clearTestData()`** deletes every data row from all four tabs and keeps the
  headers. Use it to throw away your own test records before class.
- **`archiveSection()`** copies the current rows into `dogs_archive`,
  `shakes_archive`, `focals_archive` and `gates_archive`, stamping each with the
  date and time, then clears the live tabs. Use it between class sections: each
  section starts with a clean slate and the records accumulate for a pooled
  analysis across sections and years, which is what gives the study enough
  statistical power to answer the question.

Two things the clearing functions do not touch:

- **Dog photos** stay in the "PackTrack dog photos" folder in your Drive. Delete
  that folder's contents by hand if you want them gone. Archived rows keep
  working photo links as long as the files are still there.
- **Phones that still have queued records.** If a test phone's header shows a
  red "queued" count, those records are waiting in that phone's browser and will
  upload the next time it has signal, reappearing after you cleared. Before
  clearing, open the page on each test phone with a connection and wait for
  "synced", or clear that site's data in the phone's browser settings.

You can also just delete rows directly in the Google Sheet. Keep row 1, the
header. The pages pick up the change within about ten seconds.

## Freezing the study and sharing it

Closing the dataset takes two changes, and the one that matters is on the
Google side. Changing only the web page is cosmetic: the endpoint URL is
visible in the page source, so anyone who looked could still post records to
it. Lock the endpoint and it does not matter what the page does.

### Option 1: lock the endpoint, keep the page reading live (about 3 minutes)

1. In `code.gs`, `LOCKED` is already set to `true` near the top. Paste the new
   `code.gs` over the old one and save.
2. **Redeploy, or nothing changes.** Deploy -> Manage deployments -> pencil
   icon -> Version: **New version** -> Deploy. The live endpoint keeps serving
   whatever version was last deployed, so saving the file alone has no effect.
   This is different from `clearTestData()` and `archiveSection()`, which run
   in the editor and never needed a redeploy.
3. In `packtrack.html`, `FROZEN` is already set to `true`. Upload it.
4. Check it: open the page, go to the Dogs tab, and confirm the form is greyed
   out with an "Archived record" banner, while the Results and Who tabs still
   show the data.

The endpoint still answers read requests, so the page displays the dataset from
your sheet. You can still fix or curate rows in the sheet itself, and
`archiveSection()` still works from the editor.

### Option 2: cut the Google dependency entirely

Worth doing if this page should outlive the class, since it then survives you
archiving the script, changing Google accounts, or deleting the sheet.

1. Open your web app URL with `?mode=data` on the end in a browser.
2. Select all of the JSON and copy it.
3. In `packtrack.html`, find `const ARCHIVE_DATA = null;` and replace `null`
   with the pasted JSON.
4. Upload. The page now reads that snapshot and never contacts Google.
5. You can now archive the deployment outright: Deploy -> Manage deployments
   -> Archive. That permanently stops all reads and writes.

One caveat: dog photos still load from the "PackTrack dog photos" folder in
your Drive. Leave that folder in place with its link sharing on, or the
thumbnails break. To make the page fully self-contained the photos would need
to be embedded in it as well.

### A note on student phones

A phone that still has the old page open with unsent records will keep retrying
in the background. Once `LOCKED` is deployed those attempts are refused and
nothing is written, so there is no need to chase anyone down.

## Things to know

- **Anyone who has the web app URL can submit data** while the deployment is
  live, and the URL is visible in the page source. After the lab, disable it:
  Apps Script -> Deploy -> Manage deployments -> Archive. The sheet and
  photos stay in your Drive.
- **Editing the script later**: after changing `code.gs`, you must click
  Deploy -> Manage deployments -> Edit (pencil) -> Version: New version ->
  Deploy. Saving the code alone does not update the live endpoint.
- **Dog photos** are shared "anyone with the link can view" so the page can
  display them. Delete the folder after class if you want them gone.
- **Latency**: phones poll every ~10 s, so another phone's entry appears
  within about 10 s, not instantly.
- **Offline**: a phone with no signal queues its records in the browser and
  uploads them automatically when the connection returns (a red "queued"
  counter shows in the header).
- **Fixing mistakes in the field**: each phone's last three entries show at
  the bottom of its form with a Delete button. You can also edit or delete
  rows directly in the Google Sheet; the pages pick up the change on the
  next poll.
- **Clearing for a new class**: delete the data rows in all four sheet tabs
  (keep the header row).
