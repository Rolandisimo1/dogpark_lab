# Will the shake-off lab work? Simulation results

Simulated 17 teams of two students, 25 dogs, and 80 minutes of data collection,
repeated over hundreds of independent "park-days". Each simulated dog has a
second-by-second behavior stream built from bouts of play, social, person,
self-directed and alone behavior (mean bout 33 s). Shakes are placed on behavior
boundaries 75% of the time, which is the hypothesis being tested, and students
detect, code and mis-code them with realistic error.

Terms used below:

- **Power** is the percentage of park-days on which the test comes out
  statistically significant (p < 0.05) when the hypothesis is actually true. A
  power of 55% means the lab finds the effect on roughly half of the afternoons
  it could be run.
- **False positive rate** is the percentage of park-days on which the test comes
  out significant when the hypothesis is false. It should be near 5%.
- **Shake%** is the percentage of shake windows in which the dog's behavior
  category differed from the start of the window to its end. **Ctrl%** is the
  same quantity for Team B's control windows.

## 1. The design had a bug: the control window was twice as long as the shake window

The shake form compares behavior at the shake to behavior 10 s later. The focal
form compared behavior now to behavior 20 s later. A dog has twice as long to
change behavior in a 20 s window, so the control rate was inflated by
construction.

| Design | Shake% | Ctrl% | False positive rate | Power |
|---|---|---|---|---|
| Focal window 20 s (as originally built) | 58 | 37 | **17%** | 15% |
| Focal window 10 s (matched) | 56 | 23 | 7% | **54%** |

With the 20 s window the test fired a false positive on 17% of park-days, and
the false result pointed the wrong way: shakes appeared to mark transitions
*less* often than chance. It also cut power from 54% to 15%. The focal window is
now 10 s, so both sides compare behavior at a moment to behavior 10 s later.

## 2. Duplicate records manufacture significance

Several teams scanning the whole park record the same shake. Nine scanning teams
produced 37 records from about 10 real shakes.

| Handling | Records used | Power |
|---|---|---|
| Sectors assigned (each team owns a zone) | 8.0 | 52% |
| Whole park, duplicates removed | 9.9 | 62% |
| Whole park, duplicates left in | 36.6 | **86%** |

That 86% is not real power. Duplicates of one event are not independent
observations, and leaving them in shrinks the confidence interval around a
sample that has not grown. The Results tab now drops any record of the same
registered dog logged within 20 s of another, reports how many it dropped, and
keeps the duplicates only for the inter-observer reliability check.

## 3. Expect a coin flip on the main test from one class

The binding constraint is how many shakes actually happen. At the rate implied
by Bryce et al. (0.6 shakes per dog-hour), about 13 shakes occur park-wide in 80
minutes and students record 8 of them.

| Real shake rate | Shakes recorded | Power |
|---|---|---|
| 0.3 per dog-hour | 5.5 | 27% |
| 0.6 per dog-hour (literature estimate) | 8.4 | 47% |
| 1.2 per dog-hour | 13.8 | 92% |
| 2.0 per dog-hour | 21.2 | 100% |

Pooling classes fixes this, and the app already accumulates into one sheet:

| Data pooled | Power |
|---|---|
| One class | 59% |
| Two sections | 82% |
| Three sections | 93% |
| Four sections | 99% |

## 4. Team allocation barely matters, because focal windows are superabundant

Two focal teams already produce 104 control windows, far more than the test
needs. Shake records are capped by the park, not by the number of watchers.

| Allocation | Shakes | Controls | Power |
|---|---|---|---|
| A=13 shake, B=2 focal, C=2 gate | 7.9 | 104 | 62% |
| A=9, B=4, C=4 | 8.6 | 208 | 48% |
| A=6, B=6, C=5 | 7.9 | 312 | 55% |
| A=4, B=9, C=4 | 8.9 | 468 | 63% |

Differences of this size are simulation noise. Allocate for teaching, not for
power: rotate all 17 teams through all three stations.

## 5. The gate station needs only two or three teams, and arrivals, not dogs

| Gate teams | Arrivals captured (of ~13) |
|---|---|
| 1 | 8.4 |
| 2 | 12.0 |
| 3 | 12.8 |
| 4 | 13.0 |

In a scenario where 20 of the 25 dogs were already present at the start, only 5
dogs arrived during the session and gate trials collapsed from 13 to 5. Run the
lab during an arrival window, not when the park is already full.

## 6. A paired gate control was tested and rejected

Watching each entering dog for a second 5-minute "settled" window gives a
within-dog control: 45% of dogs shook on arrival versus 4% in the settled
window. With about 11 paired trials, McNemar's exact test reached significance on
only 27% of park-days, because it uses just the discordant pairs (about 5 of
them). Across two sections it reaches 76%. The extra field complexity and the
backend change were not worth 27%, so the gate stays descriptive for now:
percentage of entering dogs that shook, with a latency distribution.

## What was changed in the app

1. Focal window cut from 20 s to 10 s so it matches the shake window.
2. The shake form's AFTER prompt now asks for behavior at the 10 s beep, an
   instant, matching the focal coding.
3. Duplicate shake records are dropped from every test, with a note reporting
   how many, and retained for the reliability check.
4. Shake rate per dog-hour now scales from 10 s windows.

## What to tell the students

The honest framing: one afternoon has about a 50% chance of a significant result
even if the hypothesis is true. A non-significant result is the expected outcome
half the time and is not a failed lab. The descriptive effect will be visible
regardless, and the shelter discussion of why n matters is worth more than a
p-value. Pooling sections across years turns the exercise into a dataset that
could answer the question properly.

## Files

- `sim3.py` park, behavior streams, observers, and the statistics
- `run3.py`, `run4.py` the reported runs
