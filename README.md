# PackTrack

A phone-based field lab for teaching animal behavior sampling, built for an
undergraduate mammalogy class and run at a dog park. Students use the standard
observation methods of primate field studies to collect real data on a
published hypothesis, then analyze the results together before they leave.

One web page holds everything: the teaching material, three data-entry forms,
and a live analysis dashboard. Students open a URL. There are no accounts and
no app to install. Records go to a Google Sheet you own.

## The study

In 2024, Bryce, Nurkin and Horowitz recorded 120 full-body shakes from 96 dogs
at a New York City dog run and coded each dog's behavior before and after.
Behavior differed across the shake in 107 of 120 events, and they concluded
that shaking marks a transition between activities
([*Animals* 14:3248](https://www.mdpi.com/2076-2615/14/22/3248), open access).

They collected no control sample, so they could not say whether behavior
changes around shakes more often than it changes in any ordinary window of
time. A class can collect that control in an afternoon, which turns the lab
from a demonstration into a test:

> **Do shakes sit at behavioral transitions more often than chance?**

## What the students do

Three stations run at once, each using a different sampling method from
Altmann (1974):

| Station | Method | What it collects |
|---|---|---|
| **Dogs** | Individual identification | A photo registry so every record names an individual |
| **Shake** | All-occurrence sampling | Every shake seen, with behavior before and 10 s after |
| **Focal** | Focal-animal sampling | Random 10 s windows: the control the original study lacks |
| **Gate** | All-occurrence at a predictable transition | Does an entering dog shake within 5 minutes of leash-off |

The Results tab runs the comparison live: a two-proportion test of shake
windows against control windows, with the published NYC figure plotted
alongside for reference. A separate tab builds per-dog behavioral profiles and
uses them to teach animal personality and repeatability.

## Files

| File | What it is |
|---|---|
| `packtrack.html` | The entire app. One self-contained page; upload it to any web host. |
| `code.gs` | Google Apps Script backend. Receives records and stores them in a Google Sheet. |
| `SETUP.md` | Full setup, pre-class testing checklist, clearing data, and freezing the study. |
| `simulation/` | A feasibility simulation of the whole lab, and what it found. |

## Quick start

About 10 minutes. `SETUP.md` has the detail and the troubleshooting.

1. Create a blank Google Sheet.
2. Extensions → Apps Script. Delete the starter code, paste in `code.gs`, save.
3. Select the `setup` function in the toolbar and click **Run**. Approve the
   authorization prompt. This creates the four data tabs and a Drive folder for
   dog photos.
4. **Deploy → New deployment → Web app.** Execute as **Me**, Who has access
   **Anyone**. Copy the web app URL.
5. Open `packtrack.html` in a text editor and replace
   `PASTE_YOUR_WEB_APP_URL_HERE` near the top of the script with that URL.
6. Upload `packtrack.html` to your web host.
7. Open the page with `?mode=data` appended to your Apps Script URL in a
   private browser window. You should see JSON beginning `{"ok":true`. A
   sign-in page instead means students will not be able to submit; fix the
   access setting in step 4.

Before class, run the test checklist in `SETUP.md`. The step that matters most
is registering a dog on one phone and confirming it appears on a second.

## Running the lab

Three hours, of which about 80 minutes is data collection. With 34 students in
17 pairs, a workable split is 7 pairs on shake scanning (one per sector of the
park), 6 on focal windows, 2 at the gate, and 2 deliberately double-covering a
sector so the class can measure inter-observer agreement. Swap the shake and
focal teams at the midpoint so everyone runs both methods.

Assign sectors for shake scanning. Several teams scanning the whole park record
the same shake repeatedly; the analysis drops duplicates, so the extra effort
is wasted.

Run the lab when dogs are still arriving. In a simulated park where most dogs
were already present at the start, gate trials fell from 13 to 5.

## What to expect from the data

The `simulation/` directory contains a model of the park, the dogs' behavior
streams, and the students, run over hundreds of simulated class sessions. Two
findings shaped the design, and one should shape your expectations:

- The control window must be the same length as the shake window. An earlier
  version compared a 10 s shake window against a 20 s control window, which
  produced a significant result in the wrong direction on 17% of simulated
  sessions.
- Duplicate records inflate significance. Nine scanning teams produced 37
  records from about 10 real shakes; left in, the test reached significance on
  86% of sessions, which is not real power.
- **One class is roughly a coin flip.** At the shake rate implied by the
  published study, about 13 shakes occur park-wide in 80 minutes and students
  record 8, giving about 50% power. A non-significant result is the expected
  outcome half the time and is not a failed lab. Pooling two sections reaches
  82%; three reaches 93%.

`archiveSection()` in `code.gs` moves each section's records into archive tabs
and clears the live ones, so sections accumulate into a pooled dataset while
each class starts clean.

## Freezing a finished study

To publish results without leaving the dataset open: set `var LOCKED = true` in
`code.gs` and redeploy a new version, and set `const FROZEN = true` in
`packtrack.html`. The page then displays the data and the teaching material
with every entry control disabled. Optionally paste the contents of your
`?mode=data` response into `ARCHIVE_DATA` in the page, which removes the
dependency on Google entirely. `SETUP.md` has both procedures.

## Adapting it

The ethogram, the behavior categories and the forms are plain HTML and
JavaScript in one file, with no build step. The same structure would work for
any short observational study where a class needs an event sampler, a focal
sampler and a live analysis: birds at a feeder, squirrels on a quad, visitors
at a zoo exhibit.

## Credits

The study design replicates and extends Bryce, C.M., Nurkin, N. and Horowitz,
A. (2024), *Animals* 14:3248. The sampling methods are from Altmann, J. (1974),
Observational study of behavior: sampling methods, *Behaviour* 49:227-267. The
personality material draws on Réale et al. (2007) *Biological Reviews*
82:291-318, Sih et al. (2004) *TREE* 19:372-378, and Bell et al. (2009)
*Animal Behaviour* 77:771-783.

Built for a mammalogy course at NC State University. Add a license file before
sharing if you want others to reuse it on defined terms.
