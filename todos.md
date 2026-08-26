Update Option 4 only by redesigning the current right-side AskTD interaction as one polished business question, one direct answer, and one elegant data chart.

This instruction supersedes the previous multi-question carousel requirement.

Do not modify any other poster option.

Objective

Replace the current generic Q&A with a realistic demonstration of how AskTD answers a business question using a clear written insight and a supporting visualization.

Show only one fixed question-and-answer example. Do not add rotation, navigation dots, counters, timers, or carousel controls.

1. Use this exact example

Status label

ILLUSTRATIVE DEMO · SYNTHETIC DATA

This label must be visible but visually restrained. It must be clear that the values are not production results.

Question

Under YOU ASKED, display:

What is driving deposit growth this quarter?

Answer

Under ASKTD ANSWERED, display:

High-Interest Savings and Term Deposits are the primary drivers, together contributing 78% of the simulated quarterly increase.

Keep the answer concise, prominent, and readable from a distance.

2. Add one meaningful chart

Below the answer, create a premium horizontal contribution chart titled:

Share of simulated deposit growth

Use this synthetic dataset:

* High-Interest Savings — 46%
* Term Deposits — 32%
* Everyday Savings — 22%

The three values must total 100%.

Chart design

Create an elegant horizontal bar chart with:

* Rounded bar ends
* Direct category and percentage labels
* TD green for the leading category
* Deep emerald for the second category
* A softer muted green for the third category
* Consistent bar height and spacing
* No unnecessary legend
* No heavy gridlines
* No axis border
* No tooltip dependency
* No fake trend line
* No decorative chart elements without meaning

Use subtle entrance animation for screen only:

* Bars grow once from left to right
* Duration approximately 600–800ms
* Calm easing
* No repeated animation

Disable the animation in print and under prefers-reduced-motion.

Use inline SVG or the project’s existing chart implementation. Prefer inline SVG if it provides sharper and more deterministic PDF output. Do not add a large charting dependency solely for this visualization.

3. Include the source label

Below the chart, display:

Source: Synthetic AskTD demonstration data

The source must remain legible in screen and PDF output.

Do not use a verified-production-data icon. A small information or demonstration indicator is acceptable.

4. Refine the product surface

Keep the interaction as one unified premium AskTD surface.

Organize it into this visual hierarchy:

1. Illustrative-demo label
2. “YOU ASKED”
3. Business question
4. Subtle divider
5. “ASKTD ANSWERED”
6. Direct answer
7. Contribution chart
8. Synthetic-data source

Use:

* One large rounded surface
* Subtle translucent border
* Restrained layered shadow
* Generous internal spacing
* Clear alignment
* Excellent contrast
* Crisp inline SVG icons
* Stable dimensions

Do not split the content into separate cards.

Ensure the answer and chart fit naturally without shrinking the typography excessively.

5. Preserve the rest of Option 4

Keep unchanged:

* The TD and AskTD brand lockup
* Stop searching dashboards. Just ask.
* Trusted data. Instant insights. Better decisions.
* Ask us a real business question.
* The four benefits along the bottom
* The existing premium green background
* Fit to Screen
* Reset Zoom
* Print / Save as PDF

Do not add:

* Additional questions
* Multiple charts
* Dashboard panels
* KPI cards
* White footer containers
* Technical workflows
* Architecture diagrams
* Production or customer data

6. Print requirements

For Print / Save as PDF:

* Show the same fixed question, answer, and chart.
* Disable all animation.
* Preserve chart colours.
* Keep SVG text and bars sharp.
* Hide preview controls.
* Ensure the full answer and every percentage are visible.
* Prevent clipping or overflow.
* Keep the poster on one landscape page.

7. Mandatory visual validation

After implementation:

1. Run the application and open Option 4.
2. Render the poster at 1600 × 1120.
3. Inspect the full-size rendering.
4. Inspect it at approximately 25% thumbnail size.
5. Confirm the question is immediately understandable.
6. Confirm the answer directly addresses the question.
7. Confirm the chart visually supports the answer.
8. Verify that 46% + 32% equals the stated 78%.
9. Verify that all three chart values total 100%.
10. Confirm the synthetic-data label is visible.
11. Test reduced-motion behavior.
12. Test Print / Save as PDF.
13. Confirm the chart remains sharp in the PDF.
14. Perform one refinement pass for typography, spacing, chart proportions, and visual balance.
15. Confirm all other poster options remain unchanged.

Implement the enhancement fully. Do not stop after describing recommendations.

Finally, report:

* Files changed
* Q&A content implemented
* Chart implementation method
* Screen validation completed
* Print/PDF validation completed
* Confirmation that only synthetic demonstration data was used
* Confirmation that other poster options were preserved
