Act as a senior brand designer, creative director, and front-end engineer.

Completely redesign the existing AskTD Business Poster HTML page into a premium, memorable product-launch poster.

This is not a small CSS cleanup. The current composition still looks like a PowerPoint slide because it uses:

* A rigid 50/50 split
* A large rectangular green panel
* Four equal feature cards
* Repetitive headings
* Conventional slide spacing
* Too many boxed elements
* No strong visual story
* No sense of movement, depth, or product experience

Do not preserve that composition.

Preserve only:

* The official TD/AskTD branding
* The approved business message
* The landscape poster dimensions
* Fit to Screen
* Reset Zoom
* Print / Save as PDF
* Print-quality output

Creative direction: “One Question. One Trusted Answer.”

Create a bold, asymmetric editorial composition that feels like:

* A premium fintech product campaign
* A modern product-launch landing page
* A high-end conference poster
* Confident, intelligent, minimal, and unmistakably TD

It must not look like:

* PowerPoint
* A corporate template
* A dashboard
* A technical architecture diagram
* A four-card feature slide
* A dense brochure
* Generic AI-generated marketing material

1. Replace the rigid split layout

Remove the straight 50/50 white-and-green division.

Create a full-canvas composition using:

* A warm off-white base
* A large organic or curved TD-green visual field entering from the upper-right and flowing toward the lower-right
* An asymmetric boundary created with a print-safe inline SVG, CSS pseudo-element, or carefully tested clip path
* A subtle deep-green gradient for depth
* Soft radial light or a restrained dot/data texture at very low opacity

The green area must feel integrated into the overall composition—not like a separate PowerPoint column.

Do not place the content inside one large green rectangle.

2. Create one dominant focal point

The headline must become the visual hero.

Use this exact copy:

Stop searching dashboards.
Just ask.

Typography direction:

* Oversized editorial typography
* Strong weight
* Tight letter spacing
* Short, deliberate line breaks
* Dark charcoal for “Stop searching dashboards.”
* TD green for “Just ask.”
* Make the headline large enough to remain powerful when the poster is viewed as a thumbnail
* Do not center-align it
* Do not place it inside a box

Use responsive typography with clamp() and carefully controlled line length.

The headline should feel more like a campaign statement than a slide title.

3. Simplify the supporting message

Directly below the headline, use:

Trusted Data. Instant Insights. Better Decisions.

Treat this as a strong campaign line, not another paragraph.

Below it, include only this short supporting sentence:

Ask what matters to your business. Get one clear answer grounded in authoritative data.

Remove unnecessary explanatory text.

4. Introduce one memorable product moment

Create one premium, floating question-and-answer composition that visually demonstrates AskTD without showing a full dashboard.

Use a large, elegant question bubble:

What changed this quarter—and why?

Connect it visually to one refined answer card:

One clear answer, grounded in authoritative data.

The answer card may include one subtle abstract insight visualization, such as:

* A minimal trend line
* Three restrained data points
* A small insight spark
* A simple confidence/check indicator

Do not display fake KPIs, percentages, financial claims, customer data, detailed charts, or a complete dashboard.

The question and answer should feel like one seamless product interaction.

Use:

* Generous padding
* Refined typography
* Soft layered depth
* One subtle accent glow
* A controlled shadow
* Clean inline SVG icons
* No emojis
* No excessive glassmorphism

Allow this composition to overlap the curved green field slightly so the two halves of the poster visually connect.

5. Remove the four feature cards

Delete the current 2×2 card grid completely.

Do not replace it with another grid.

Present the four business benefits as a refined editorial proof strip or vertical typographic sequence with no surrounding boxes:

01 — Faster answers
Clear answers in seconds

02 — Trusted data
Authoritative and governed

03 — Actionable insights
Trends, drivers, and visuals

04 — Less effort
Fewer reports and less dashboard searching

Possible presentation:

* A single horizontal proof strip near the bottom
* Or a vertically staggered sequence integrated into the green visual field
* Use thin separators, large numbers, and excellent typography
* Avoid rectangular cards
* Avoid repeated icons if the numbers already provide sufficient structure
* Keep descriptions short

This section must feel like editorial information design, not a PowerPoint feature table.

6. Add a strong campaign-level micro-message

Within the green visual field, introduce one oversized, low-opacity typographic element such as:

ONE

or:

ASK → ANSWER

Use it as a background design element, not primary content.

It should:

* Create visual depth
* Reinforce the product idea
* Remain subtle enough not to affect readability
* Use approximately 4–8% opacity
* Never compete with the main headline

Do not add multiple decorative words.

7. Strengthen the brand treatment

Keep the official TD logo undistorted.

Present AskTD confidently beside it.

Do not use an ordinary PowerPoint-style underline below AskTD.

Instead, use one refined brand detail, such as:

* A small green indicator
* A narrow accent bar
* A subtle “Conversational Analytics” descriptor
* A carefully spaced wordmark treatment

Use only one of these options.

The top brand area should feel deliberate, clean, and premium.

8. Refine the call to action

Use this exact CTA:

Ask us a real business question.

Make it part of the composition rather than leaving it isolated at the bottom of a large empty area.

Use a distinctive but restrained treatment:

* A horizontal green rule flowing into the text
* A small conversation mark
* Or a minimal outlined prompt capsule

It must not look like a web button.

9. Create depth without creating clutter

Use depth intentionally through:

* Layered green tones
* One curved background form
* One floating question/answer interaction
* Subtle transparency
* Controlled shadows
* Thin editorial rules
* Slightly overlapping composition
* Strong contrast between large and small typography

Do not use:

* Multiple boxes
* Generic card grids
* Heavy borders
* Large dashboard mockups
* Stock photos
* People sitting around a monitor
* Neon cyberpunk effects
* Excessive glow
* Random particles
* Architecture flows
* Technical processing steps
* Long product descriptions
* Tiny text
* Decorative elements without purpose

Every visible element must support the “one question, one trusted answer” story.

10. Make the screen version feel alive

Because this is an HTML experience, add extremely subtle screen-only motion:

* A slow ambient gradient drift
* A 2–3 pixel floating movement on the question card
* A restrained light sweep or pulse on the answer indicator
* Smooth entrance sequencing when the poster first loads

Motion rules:

* Keep animations slow and premium
* Do not use bouncing, spinning, flashing, or dramatic movement
* Disable all animation in print
* Disable or reduce motion under prefers-reduced-motion
* The static version must remain equally polished

The motion should make the HTML page feel alive without looking like an animated presentation.

11. Use a disciplined visual system

Define reusable CSS variables for:

* TD green
* Deep green
* Light green
* Warm off-white
* Charcoal
* Muted text
* Spacing
* Border radius
* Shadows

Suggested palette direction:

* Primary TD green: approximately #008A00
* Deep green: approximately #004C24
* Warm off-white: approximately #F6F7F2
* Charcoal: approximately #111814

Verify existing brand variables first and reuse official project values where available.

Use a modern system font stack already available in the project. Do not load unnecessary external font dependencies.

12. Protect print quality

The final poster must print cleanly on one landscape page.

Ensure:

* Exact landscape aspect ratio is preserved
* Background graphics print correctly
* print-color-adjust: exact is applied
* Preview controls are hidden in print
* No content is clipped
* No text becomes too small
* Shadows remain subtle in PDF
* Animations stop in print
* SVG shapes remain sharp
* All critical text stays inside safe print margins

Test both browser preview and Print / Save as PDF.

13. Implementation approach

First inspect the current HTML, CSS, JavaScript, and poster rendering logic.

Then:

1. Remove the current slide-like visual structure.
2. Preserve working preview and print functionality.
3. Rebuild the poster composition using semantic HTML and maintainable CSS.
4. Use inline SVG only where it materially improves the curved background or insight visual.
5. Avoid adding a new UI framework.
6. Avoid changing unrelated pages or files.
7. Do not stop after describing a concept—implement it fully.

14. Mandatory visual QA loop

After the first implementation:

1. Run the application.
2. Render the poster at 1600 × 1120.
3. Capture or inspect the page at full size.
4. Inspect it again at approximately 25% thumbnail size.
5. Ask:
    * Does it still look like PowerPoint?
    * Is there one unmistakable focal point?
    * Is the product idea understood within three seconds?
    * Does the eye move naturally from headline to question to answer to benefits?
    * Are there too many rectangles?
    * Is any text too small?
    * Does the green shape feel integrated rather than divided?
6. Make a second visual refinement pass.
7. Repeat until the composition feels like a premium campaign poster.

Acceptance criteria

The redesign is complete only when:

* The rigid 50/50 split is gone
* The 2×2 feature-card grid is gone
* Duplicate headings are gone
* The poster has one dominant focal point
* The question-to-answer concept is immediately understandable
* The page looks intentionally designed at both full size and thumbnail size
* It feels like a premium AskTD product campaign
* It does not resemble a PowerPoint slide
* Print / Save as PDF still works perfectly
* No unrelated files were modified

Finally, report:

* Files changed
* Major structural changes
* Visual design decisions
* Screen and print validation completed
* Any remaining constraints

Do not make another conservative iteration of the existing layout. Commit to the new art direction and deliver a visibly different, premium result.
