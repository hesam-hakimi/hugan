Update the current Option 4 AskTD poster by replacing the generic product question on the right with a small set of genuine business question-and-answer examples.

This is a focused enhancement to the existing Option 4 implementation. Preserve the approved layout, visual theme, headline, tagline, benefit row, preview controls, and print behavior.

Do not modify the other poster options.

Objective

The current question:

How can AskTD help me understand business performance?

is too generic and sounds like product documentation.

Replace it with real business-style analytical questions that demonstrate how someone would genuinely use AskTD.

The screen version should rotate through up to three approved question-and-answer examples.

The printed/PDF version should display only the strongest approved example.

1. Find approved question-and-answer content first

Before changing the poster content, inspect the current project for:

* Approved AskTD demo questions
* Synthetic-data examples
* Existing fixtures
* Mock API responses
* Demo screenshots
* Approved sample reports
* Existing static Q&A content
* Documentation containing validated examples

Use only content that is clearly approved for demonstration or based on synthetic data.

Do not:

* Query production systems
* Use production credentials
* Include customer information
* Include PII or PCI data
* Copy confidential business data
* Fabricate percentages or financial results
* Invent regional or customer performance claims
* Alter the meaning of an approved answer

If only one or two approved Q&A pairs are available, use only those. Do not fabricate a third example merely to complete the carousel.

If no approved business answer is available, implement the rotation framework but keep the current safe product-capability example as a temporary fallback and clearly report that approved demo answers are still required.

2. Preferred business questions

Prefer the following questions when matching approved demo answers exist:

Question 1

What is driving deposit growth this quarter?

Question 2

Which customer segments contributed most to the change?

Question 3

Where are we seeing the largest regional variance?

These questions form a natural analytical sequence:

1. Understand what changed
2. Investigate who or what drove it
3. Explore where the difference occurred

However, the accuracy of the answer is more important than preserving these exact questions. If the repository contains different approved business questions with complete answers, use the approved pairs instead.

Never attach an unrelated answer to one of these questions.

3. Create structured content

Represent each approved example as structured data rather than duplicating HTML.

Use a structure similar to:

{
  question: "...",
  answer: "...",
  drivers: ["...", "..."],
  sourceLabel: "...",
  chartData: [],
  isApprovedDemo: true
}

Requirements:

* question must contain the complete user question.
* answer must directly answer that question.
* drivers should be included only when supported by approved content.
* sourceLabel must accurately identify the approved demo or synthetic source.
* chartData should be included only when actual approved demo values exist.
* Do not create fake chart points merely for decoration.

Keep the content deterministic so screen and PDF rendering do not depend on a live API call.

4. Keep one question visible at a time

Do not show three question cards simultaneously.

The poster must retain one clear focal point.

Within the existing right-side product surface, show:

YOU ASKED

followed by the currently selected question.

Then show:

ASKTD ANSWERED

followed by its matching approved answer.

Only one complete question-and-answer pair should be visible at any moment.

Maintain a fixed container size across all examples to prevent the poster from shifting when the content changes.

5. Add a restrained rotation experience

For the screen version:

* Rotate to the next approved example approximately every 8–10 seconds.
* Use a subtle 350–500ms crossfade.
* Do not slide large panels horizontally.
* Do not bounce, flip, spin, or use dramatic carousel effects.
* Pause rotation while the user hovers over or focuses within the Q&A surface.
* Restart carefully after interaction.
* Avoid visible layout movement.

Add a minimal status indicator such as:

01 / 03

or three very small navigation dots.

The indicator should remain secondary and must not make the design resemble a slideshow.

Allow manual navigation using:

* Previous/next controls with accessible labels
* Keyboard left/right arrows when the Q&A surface has focus
* Clickable indicator dots if appropriate

Keep controls visually subtle.

6. Respect reduced-motion settings

Under prefers-reduced-motion: reduce:

* Disable automatic rotation.
* Disable transition animations.
* Show the first approved example.
* Preserve manual navigation if it remains accessible.

7. Configure the print/PDF version

The print version must not rotate or display carousel controls.

Inside @media print:

* Disable all timers and transitions.
* Hide navigation dots, counters, and previous/next controls.
* Display exactly one approved Q&A pair.
* Use the strongest approved example as the print default.
* Prefer “What is driving deposit growth this quarter?” only when a matching approved answer exists.
* Otherwise use the strongest available approved demo pair.
* Ensure the complete answer fits without clipping.
* Preserve background colours and print-safe contrast.

The PDF must remain deterministic: printing the same page should always produce the same selected example.

8. Present a complete answer

Each response should feel like a genuine AskTD answer, not a marketing statement.

The answer area may include:

* One concise answer of approximately one or two sentences
* Two or three validated key drivers
* A small trusted-source indicator
* One restrained chart only when approved chart data is available

Do not use the generic sentence:

“One clear answer, grounded in authoritative data.”

as the entire answer.

That phrase may appear as a supporting trust statement, but it does not replace the actual answer.

If no approved numeric data exists, omit the chart rather than drawing an invented trend.

9. Preserve the premium Option 4 design

Keep:

* The existing premium green visual field
* The Apple-inspired simplicity
* The headline:
    Stop searching dashboards.
    Just ask.
* The tagline:
    Trusted data. Instant insights. Better decisions.
* The four business benefits at the bottom
* The CTA:
    Ask us a real business question.

Do not add:

* Multiple visible Q&A cards
* A large carousel container
* Dashboard screenshots
* Technical workflows
* Architecture diagrams
* Additional explanatory paragraphs
* A white footer bar
* Fake data visualizations

10. Improve readability

Ensure every question and answer remains readable at the intended 1600 × 1120 poster size.

Use:

* Clear distinction between question and answer
* Strong answer typography
* Sufficient line height
* Consistent internal spacing
* High contrast
* A stable Q&A surface height

Handle longer content gracefully without:

* Shrinking text excessively
* Clipping
* Overflow
* Uneven card height
* Moving the feature row

If an approved answer is too long, create a concise poster-safe summary without changing its facts. Preserve the full original approved answer in a source comment or content file for traceability.

11. Validate the implementation

After implementation:

1. Run the application.
2. Open Option 4.
3. Confirm that only approved Q&A examples are used.
4. Confirm that every answer matches its question.
5. Observe at least two complete automatic rotation cycles.
6. Test manual navigation.
7. Test keyboard navigation.
8. Test pause on hover and focus.
9. Test reduced-motion behavior.
10. Confirm there is no layout shift.
11. Render at 1600 × 1120.
12. Inspect at approximately 25% thumbnail size.
13. Test Print / Save as PDF.
14. Confirm the PDF always displays the same approved example.
15. Confirm carousel controls are absent from print.
16. Confirm other poster options remain unchanged.
17. Check the browser console for errors.

Acceptance criteria

The enhancement is complete only when:

* The generic product question has been replaced by real business-style questions.
* Every displayed question has a matching approved answer.
* No confidential or fabricated data is present.
* Only one Q&A pair is visible at a time.
* The screen version rotates calmly through the approved examples.
* The printed version displays one fixed example.
* The design remains simple and premium.
* No layout shifting or text clipping occurs.
* Option 4’s existing headline, tagline, benefits, and CTA remain intact.
* All other poster options remain unchanged.

Implement and validate the enhancement fully.

Finally, report:

* Files changed
* Q&A examples found
* Source of each approved example
* Whether synthetic/demo data was used
* Which example is used for print
* Screen rotation validation
* Print/PDF validation
* Confirmation that no fabricated data was introduced
