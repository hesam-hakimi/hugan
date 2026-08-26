Refine Option 4 only based on the latest visual and content review.

Do not redesign the poster or modify any other poster option. Preserve the current layout, green light field, benefit row, CTA, AskTD card, preview controls, and print functionality.

This task has two focused objectives:

1. Make the banking question, answer, and chart analytically consistent.
2. Replace and correctly typeset the main headline so no letters touch or overlap.

1. Replace the main headline

Replace:

Stop searching dashboards.
Just ask.

with:

Stop searching
for answers.
Just ask.

Use these exact manually controlled line breaks.

This wording is intentionally broader than “dashboards” or “reports.” It communicates that AskTD helps users find answers without restricting the product to one type of analytical content.

Do not allow the browser to determine the line wrapping.

Use separate block-level elements:

<h1
  class="hero-title"
  aria-label="Stop searching for answers. Just ask."
>
  <span class="hero-title__line">Stop searching</span>
  <span class="hero-title__line">for answers.</span>
  <span class="hero-title__line hero-title__accent">Just ask.</span>
</h1>

2. Fix the headline collision

The current headline has insufficient vertical spacing. The descenders in letters such as p in “Stop” and g in “searching” enter the next line.

This is a typography defect and must not be solved merely by reducing the font size.

Use independently spaced headline lines:

.hero-title {
  display: grid;
  justify-items: start;
  row-gap: 0.08em;
  margin: 0;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.035em;
  color: var(--charcoal);
}
.hero-title__line {
  display: block;
  line-height: 1;
  white-space: nowrap;
}
.hero-title__accent {
  margin-top: 0.14em;
  color: var(--td-green);
}

Adapt the selectors to the existing project structure.

Requirements:

* Preserve approximately the current headline size.
* Do not use a headline line-height below 0.98.
* Do not use negative vertical margins.
* Do not use translateY or absolute positioning to tighten the lines.
* Do not tighten tracking beyond approximately -0.04em.
* Maintain a visible optical gap between the first two lines.
* Provide slightly more separation before the green “Just ask.” line.
* Keep all three lines aligned with the TD/AskTD brand lockup.
* Preserve exactly the same line breaks in screen and print output.

3. Correct the business question

Replace:

What is driving deposit growth this quarter?

with:

Which deposit products contributed most to this quarter’s growth?

The original question asks for causal drivers, while the chart only shows product-level contribution. The revised question accurately matches the information presented.

Keep the question to approximately two lines within the current card.

4. Correct and simplify the answer

Replace the current answer with:

High-interest savings accounts and term deposits were the largest contributors, accounting for 78% of the simulated increase.

Use sentence case.

Do not capitalize the category names as though they were official branded TD product names.

5. Refine the chart terminology

Change the chart title to:

Contribution to simulated deposit growth

Use these labels and values:

* High-interest savings accounts — 46%
* Term deposits — 32%
* Everyday savings accounts — 22%

Important semantic rule:

The percentages represent each product category’s share of the total simulated increase. They are not individual product growth rates.

Do not describe 46%, 32%, or 22% as rates of growth.

Use one structured data source for the chart, for example:

const depositContributionData = [
  { label: "High-interest savings accounts", value: 46 },
  { label: "Term deposits", value: 32 },
  { label: "Everyday savings accounts", value: 22 }
];

Derive the 78% statement from the first two chart values instead of maintaining an unrelated hard-coded number. This prevents the written answer and chart from becoming inconsistent later.

Confirm programmatically or through validation that:

* 46 + 32 = 78
* 46 + 32 + 22 = 100

6. Preserve the synthetic-data disclosure

Keep a visible label above the question:

ILLUSTRATIVE EXAMPLE · SYNTHETIC DATA

Use this source below the chart:

Source: Synthetic AskTD demonstration data

The example must never appear to represent actual TD performance.

Do not introduce:

* Production data
* Customer data
* Confidential metrics
* Actual regional results
* Real financial claims

7. Preserve and refine the chart design

Keep the existing premium horizontal-bar presentation, but ensure:

* All labels remain readable.
* Category names do not collide with percentages.
* Percentages are right-aligned.
* Bar widths accurately represent 46%, 32%, and 22%.
* The three bars share the same baseline and scale.
* The leading bar uses TD green.
* Secondary bars use restrained green tones.
* No dashboard-style grid, axis, or legend is added.
* The chart remains sharp in PDF output.
* The chart is visually meaningful rather than merely decorative.

Do not add another chart, KPI card, trend line, or carousel.

8. Preserve all other Option 4 content

Keep unchanged:

* TD and AskTD branding
* Trusted data. Instant insights. Better decisions.
* Ask us a real business question.
* The four benefits at the bottom
* Existing premium background treatment
* Fit to Screen
* Reset Zoom
* Print / Save as PDF

Do not modify other poster options.

9. Mandatory visual validation

After implementation:

1. Render Option 4 at its native 1600 × 1120 size.
2. Inspect the headline at 100%.
3. Inspect it at the current 90% preview zoom.
4. Inspect it at approximately 25% thumbnail size.
5. Confirm that no part of p, g, y, or any other glyph touches the following line.
6. Confirm that the first two headline lines have a visible optical gap.
7. Confirm there is slightly more space before “Just ask.”
8. Verify that the headline does not reflow when using Fit to Screen or Reset Zoom.
9. Confirm that the question, answer, and chart describe the same analytical result.
10. Confirm that all chart values total 100%.
11. Confirm that the written 78% matches the first two bars.
12. Test Print / Save as PDF after fonts are fully loaded.
13. Inspect the PDF at 100% and confirm identical headline line breaks.
14. Confirm there is no clipping or overflow.
15. Perform one final refinement pass for headline spacing, chart readability, and optical alignment.

Implement the changes fully and then report:

* Files changed
* Final headline used
* Final question and answer
* How the 78% value is derived
* Screen validation completed
* PDF validation completed
* Confirmation that other poster options were preserved
