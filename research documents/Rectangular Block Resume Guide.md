# **The Ultimate Guide to Rectangular Block Resumes: Achieving Perfect Single-Line Bullet Alignment Across Screens, DPIs, and Formats**

The professional resume has undergone a radical transformation from a static list of qualifications to a sophisticated piece of document engineering. In the modern recruitment landscape, particularly within the high-stakes fintech and technology sectors, the visual presentation of data must match the technical rigor of the candidate's professional output. The "Rectangular Block" resume—a design philosophy where every bullet point forms a perfect, non-wrapping horizontal bar extending from the left margin to the right—represents the intersection of typographic precision and semantic clarity. Achieving this aesthetic requires a deep understanding of font metrics, specifically the Calibri typeface, and the utilization of responsive layout engines in HTML5/CSS3, the mathematical typesetting of LaTeX, and the structured environments of Microsoft Word. As Applicant Tracking Systems (ATS) in 2026 evolve toward AI-driven semantic matching, the structural integrity of these documents becomes paramount, ensuring that information remains machine-readable while projecting an image of meticulous authority to human recruiters.1

## **The Typography of Precision: Calibri Metrics and Glyph Mechanics**

The foundation of any rectangular block design is the mathematical understanding of the font’s horizontal metrics. Calibri, designed by Luc(as) de Groot and released as part of the Microsoft ClearType collection, was engineered specifically to improve readability on digital displays.4 Unlike monospaced fonts, Calibri is a proportional typeface, which means each character has a unique advance width. To force a bullet point to fill exactly one line without wrapping or leaving excessive whitespace, the document engineer must calculate the cumulative width of the character string and adjust the layout parameters—font size, letter spacing, and word spacing—to match the available line width.6

### **Mathematical Modeling of Font Units**

In digital typography, letters are drawn on a grid where an arbitrary number of units, known as Units per EM (UnitsPerEm), define the coordinate system. For Calibri, this value is set to 2048\.8 This resolution allows for high-fidelity rendering of the font's characteristic rounded stems and subtle curves. To determine the physical pixel width of a string at a specific point size and screen resolution, the advance widths stored in the font's hmtx table must be scaled using the following ratio:

![][image1]  
On a standard 96 DPI display at 11pt, the Maximum Digit Width (MDW)—a critical metric for layout designers—is precisely 7 pixels for Calibri.8 This value serves as a baseline for determining character density. For a resume using a 10pt base size, the "rectangular" fit requires balancing the character count against the line width. On a standard 8.5-inch page with 1-inch margins, the available 6.5-inch (468pt) text block typically accommodates 75 to 90 characters of Calibri 10pt before wrapping occurs.4

| Character Type | Representative Glyph | Advance Width (Units) | Pixel Width (10pt @ 96 DPI) |
| :------------- | :------------------- | :-------------------- | :-------------------------- |
| Narrow         | i, l, j, 1,          | 300 \- 500            | 2 \- 3 px                   |
| Standard       | a, e, o, s           | 900 \- 1100           | 6 \- 7 px                   |
| Wide           | w, m, M, W           | 1400 \- 1800          | 9 \- 11 px                  |
| Space          | (U+0020)             | 512                   | 3.33 px 13                  |
| Bullet         | (U+2022)             | 800                   | 5.2 px                      |

### **Subpixel Rendering and DPI Scalability**

Achieving a rectangular block that holds its shape across 96 DPI, 144 DPI (Retina), and 288+ DPI (4K mobile) displays requires the use of subpixel precision. Browser rendering engines like Blink (Chrome) and WebKit (Safari) use sophisticated text shapers to position glyphs at fractional pixel coordinates.7 This prevents "jitter" when the user zooms in or out. For a resume to maintain its "block" look, the document must be architected using relative units—such as rem, em, and cqi—rather than fixed pixel values. This ensures that the ratio between the font size and the container width remains constant regardless of the hardware's pixel density.14

## **The 2026 ATS Paradigm: Semantic Parsing and Structural Standards**

The "rectangular block" design is not merely an aesthetic preference but a technical optimization for modern recruitment software. By 2026, 97% of Fortune 500 companies have integrated AI-powered Applicant Tracking Systems (ATS) that utilize semantic matching rather than simple keyword searching.2 These systems prioritize the "Skills-First" model, extracting value from resumes based on context and measurable impact. The single-line rectangular bullet point is the ideal delivery vehicle for the "XYZ" bullet formula: "Accomplished \[X\] as measured by, by doing \[Z\]".1

### **The Necessity of Single-Column Layouts**

While multi-column layouts were historically popular for their aesthetic appeal, they are fundamentally incompatible with the parsing algorithms of 2026 ATS platforms. AI scanners read documents from left-to-right across the entire page width; if a document is divided into columns, the scanner may merge text from the left column into the right, creating nonsensical data fragments.1 The rectangular block approach utilizes a single-column architecture, ensuring that every experience, skill, and achievement is parsed in its intended order.18

### **Impact-Based Bullet Points and Line Density**

The shift in 2026 is away from task-based descriptions toward impact-based results. A rectangular bullet point forces the candidate to be concise, as any text wrapping to a second line breaks the block aesthetic and reduces the visual "scanability" of the document. Strategic keyword integration—where terms are woven naturally into the XYZ narrative—improves the candidate's ranking in AI-powered screening.1

| ATS Feature         | Technical Requirement            | Rectangular Block Application                |
| :------------------ | :------------------------------- | :------------------------------------------- |
| Sequential Parsing  | Single-column layout             | Ensures top-to-bottom data extraction.17     |
| Semantic Matching   | High-density keywords in context | Uses XYZ format to anchor keywords.3         |
| Machine Readability | Standard fonts (Calibri, Arial)  | Prevents OCR errors from decorative fonts.12 |
| Visual Hierarchy    | Consistent header formatting     | Identifies sections (Experience, Skills).    |

## **Engineering the Responsive Web Resume: HTML and CSS Architecture**

HTML and CSS represent the most flexible and powerful stack for creating a truly responsive rectangular block resume. Unlike traditional PDF or Word documents, a web-based resume can adapt its typography in real-time to maintain the "solid block" look on any screen, from a 4-inch smartphone to a 32-inch 4K monitor.14 This is achieved through the use of container queries, fluid typography, and advanced justification properties.

### **Base Template and Viewport Optimization**

The core of the HTML resume is a self-contained structure that uses a viewport meta tag to control scaling. The CSS must define a font stack that prioritizes Calibri while providing metrically compatible fallbacks like Arimo or Lato to ensure the line-length calculations remain accurate even on systems where Microsoft fonts are not pre-installed.5

HTML

\<\!DOCTYPE **html**\>  
\<html lang\="en"\>  
\<head\>  
 \<meta charset\="UTF-8"\>  
 \<meta name\="viewport" content\="width=device-width, initial-scale=1.0"\>  
 \<style\>  
 :root {  
 \--base-font-size: 10pt;  
 \--calibri-stack: 'Calibri', 'Arimo', sans-serif;  
 \--page-width: 8.5in;  
 \--container-padding: 5%;  
 }  
 body {  
 font-family: var(--calibri-stack);  
 font-size: var(--base-font-size);  
 display: flex;  
 justify-content: center;  
 margin: 0;  
 background-color: \#f4f4f4;  
 }  
 .resume-page {  
 background-color: white;  
 width: 100%;  
 max-width: var(--page-width);  
 min-height: 11in;  
 padding: 1in;  
 box-shadow: 0 0 10px rgba(0,0,0,0.1);  
 container-type: inline-size; /\* Enables Container Queries \*/  
 }  
 \</style\>  
\</head\>

### **Fluid Typography via clamp() and cqi**

To achieve perfect rectangularity, the font size must scale in proportion to the width of the container. Traditional viewport units (vw) are flawed because they respond to the browser window rather than the resume's specific container. The 2026 standard utilizes Container Query Units (cqi), where 1cqi is equal to 1% of the container's inline size.15 The clamp() function is then used to set a legibility floor and a professional ceiling.20

![][image2]  
This formula ensures that as the screen narrows (e.g., on a mobile device), the font size shrinks just enough to keep the 85-character bullet point on a single line. If the screen becomes too wide, the clamp prevents the font from becoming unprofessionally large, maintaining the 11pt maximum.14

### **Bullet Perfection and Non-Wrapping Enforcement**

The "Rectangular Block" aesthetic is destroyed by orphans—single words that wrap to a new line. In CSS, this is prevented by using white-space: nowrap combined with an overflow strategy. However, simple nowrap will cause text to cut off. The solution is a combination of text-align-last: justify and letter-spacing adjustments.23

CSS

ul {  
 padding-left: 0;  
 list-style: none;  
}

li {  
 width: 100%;  
 white-space: nowrap;  
 overflow: hidden;  
 text-overflow: clip;  
 text-align: justify;  
 text-align-last: justify; /\* Modern browser support for single-line blocks \*/  
}

/\* Pseudo-element hack for legacy support \*/  
li::after {  
 content: "";  
 display: inline-block;  
 width: 100%;  
}

By applying text-align-last: justify, the layout engine is forced to distribute word-spacing across the entire line, even for the final (and only) line of the paragraph. This pushes the last word of the bullet point flush against the right margin, creating the desired solid horizontal bar.23

### **Subpixel Precision and Zoom Handling**

Recruiters often zoom into documents to read fine details. Standard fluid units can fail at extreme zoom levels because of how browsers calculate the "CSS pixel" relative to the "physical pixel." To ensure the rectangular block remains intact at 200% zoom (the WCAG 2.1 accessibility standard), the CSS must incorporate a static rem or em component into the calculation to prevent the font from shrinking to zero.15

CSS

li {  
 font-size: clamp(0.75rem, 1.8cqi \+ 0.2rem, 1rem);  
 letter-spacing: \-0.01cqi; /\* Micro-adjustment for spacing \*/  
}

This hybrid unit calculation allows the text to scale with the container while respecting the user's base font settings, providing a consistent experience across all display DPIs.7

## **The Precision of LaTeX: High-Fidelity PDF Engineering**

For candidates who prioritize a static, pixel-perfect PDF that prints identically on any machine, LaTeX is the preferred engineering tool. LaTeX's "boxes and glue" model provides the most robust mechanism for line justification in existence. By using the geometry package to define the page bounds and enumitem for granular control over list formatting, a candidate can produce a resume that is typographically superior to any other format.25

### **Document Class and Calibri Integration**

To use Calibri in LaTeX, one must utilize the fontspec package and compile with the XeLaTeX or LuaLaTeX engines. This allows the document to access the system's TrueType or OpenType font files directly, ensuring the metrics used by the layout engine are identical to those used by Microsoft Word.5

Code snippet

\\documentclass\[10pt,letterpaper\]{article}  
\\usepackage\[margin=1in\]{geometry}  
\\usepackage{fontspec}  
\\setmainfont{Calibri}  
\\usepackage{xcolor}

\\usepackage{enumitem}  
\\setlist\[itemize\]{  
 nosep,  
 leftmargin=0pt,  
 itemindent=0pt,  
 labelsep=1em,  
 align=left,  
 before=\\flushleft,  
 after=\\endflushleft  
}

### **The \\leaders Command for Solid Section Blocks**

A common requirement for rectangular resumes is a horizontal bar that separates sections. While simple rules (\\hrule) can be used, the \\leaders command allows for a "smart" rectangle that fills the remaining horizontal space on a line after a heading. This creates a visually grounded "block" that guides the recruiter's eye across the page.27

Code snippet

\\newcommand{\\sectionheader}{%  
 \\par\\noindent  
 \\mbox{\\textbf{\\uppercase{\#1}}\\ } % The text of the header  
 \\textcolor{gray}{\\leaders\\vrule height 1.1ex depth \-0.1ex\\hfill} % The block  
 \\par\\vspace{6pt}  
}

### **Forcing Rectangularity in Bullet Points**

In LaTeX, a line that is naturally shorter than the page width will not be justified by default. To force a bullet point to fill the entire line, one can use the \\hfill command, but this often requires a adjustment to the \\parfillskip parameter. By setting \\parfillskip=0pt, the document engineer tells LaTeX that the final line of every paragraph must be stretched to the margin.27

Code snippet

\\newcommand{\\blockitem}{%  
 \\item {\#1\\hfill\\parfillskip=0pt\\par}  
}

This technical adjustment ensures that even if a bullet point is three words short of a full line, the inter-word spacing will be stretched mathematically to ensure the line ends exactly at the right margin, maintaining the rectangular block aesthetic.27

## **The DOCX Professional Interface: Word Optimization and VBA Automation**

Microsoft Word remains the "corporate gold standard" for resume submission due to its near-universal compatibility. However, Word's layout engine is less precise than CSS or LaTeX, often introducing unexpected wrapping when a document is opened on a system with a different default printer driver.1 To achieve "perfect" rectangular blocks in DOCX, document engineers must employ a combination of "invisible table" layouts and programmatic VBA macros.

### **The Invisible Table Layout Method**

Tables are the only way to enforce rigid horizontal constraints in Word. By placing the work experience and skills sections inside a single-column table with a fixed width, the candidate prevents the text from reflowing if the recruiter's margins are slightly different.1

1. Insert a table with one column and multiple rows.
2. Select Table Properties \> Column \> Preferred Width and set it to 6.5 inches (for 1-inch margins).
3. Under Table Properties \> Borders and Shading, set all borders to "None."
4. Set the paragraph alignment to "Justify" (Ctrl+J).

This "container" mimics the CSS inline-size query, providing a stable environment for the rectangular bullets.

### **VBA Automation for One-Line Bullet Fitting**

For a resume with many bullet points, manual adjustment of character spacing is inefficient. A VBA macro can be used to scan the document and automatically "condense" or "expand" character spacing (Font.Spacing) to ensure every bullet fits on exactly one line. This uses the ComputeStatistics(wdStatisticLines) method to detect if a paragraph has wrapped.30

VBA

Sub ForceRectangularBullets()  
 Dim para As Paragraph  
 For Each para In ActiveDocument.Paragraphs  
 ' Target only bulleted items  
 If para.Range.ListFormat.ListType \= wdListBullet Then  
 para.Alignment \= wdAlignParagraphJustify  
 ' Check if it has wrapped to 2 lines  
 Do While para.Range.ComputeStatistics(wdStatisticLines) \> 1  
 ' Reduce character spacing by 0.05 points until it fits  
 para.Range.Font.Spacing \= para.Range.Font.Spacing \- 0.05  
 Loop  
 End If  
 Next para  
End Sub

### **Character Metrics and Trimming Standards**

Programmatic optimization is most effective when the content is already close to the target length. For Calibri 10pt on a 6.5-inch line, the ideal character count (including spaces) is between 82 and 88 characters.8 Bullets shorter than 75 characters may look "gappy" when justified, while those over 92 characters will require excessive condensation, reducing legibility. A secondary macro can be used to flag bullet points that fall outside this "Rectangular Zone".33

| Line Count   | Spacing Adjustment            | Visual Result                 |
| :----------- | :---------------------------- | :---------------------------- |
| \< 75 chars  | Expand (+0.1pt to \+0.3pt)    | High legibility, slight gaps. |
| 82-88 chars  | Normal (0pt)                  | Perfect rectangular block.30  |
| 92-98 chars  | Condense (-0.1pt to \-0.25pt) | Tight, high-density block.34  |
| \> 100 chars | Error/Trim required           | Risk of illegibility.         |

## **Content Engineering: The XYZ Formula for Fintech and Technology**

The "Rectangular Block" is more than a formatting choice; it is an informational architecture. For a PM at AmEx or a Cloud Engineer, the content must be as "scalable" as the layout. This requires the use of the XYZ bullet format, which aligns perfectly with the horizontal requirements of a single-line block.3

### **Quantitative Accomplishments in a Single Line**

To achieve the 85-character target, the candidate must master the art of the "Impactful Verb." Instead of saying "I was responsible for managing a team of developers who built an AI tool," the candidate should write:

_"Led a 10-person engineering team to deploy a GenAI risk model, reducing fraud by 15% ($2.4M)."_

This sentence is exactly 84 characters. It contains the Action (Led), the Context (GenAI risk model), and the Result (reducing fraud by 15%). Typographically, it forms a solid horizontal bar in Calibri 10pt that fills the 6.5-inch page width almost perfectly.3

### **Keyword Anchoring and Semantic Clusters**

2026 ATS platforms look for "Semantic Clusters"—groups of related keywords that prove expertise. For a technology role, a bullet point should anchor these clusters within the rectangular block.

- _Cloud/DevOps Cluster:_ "Architected a multi-region AWS infrastructure using Terraform and Docker, achieving 99.99% uptime." (91 characters)
- _Fintech/PM Cluster:_ "Streamlined AmEx payment APIs for 5M+ users, increasing transaction throughput by 22% YoY." (87 characters)

By placing the most important technical keywords (AWS, Terraform, API) in the middle of the block and the results (% improvement) at the end, the candidate ensures that both the AI parser and the human recruiter capture the most critical data points during a 6-second scan.1

## **Cross-Format Comparison: Selecting the Optimal Engine**

Each document format offers distinct advantages and drawbacks in the pursuit of the rectangular block. The choice of format should be dictated by the candidate's technical proficiency and the specific requirements of the application portal.

| Metric                      | HTML/CSS                 | LaTeX                   | Microsoft Word              |
| :-------------------------- | :----------------------- | :---------------------- | :-------------------------- |
| **Responsiveness**          | Extreme (4K to Mobile)   | Low (Fixed-scale)       | Moderate (Web View)         |
| **Justification Precision** | High (Browser-dependent) | Absolute (Mathematical) | Moderate (Driver-dependent) |
| **ATS Compatibility**       | High (Semantic HTML)     | High (Vector-text)      | Universal (Standard)        |
| **Maintenance Ease**        | Moderate (CSS knowledge) | High (TeX environment)  | Low (Manual formatting)     |
| **DPI Scalability**         | Fluid (Subpixel)         | Perfect (Vector)        | Good (Raster-hinting)       |

### **The Case for HTML/CSS as the Primary Format**

For technology professionals, particularly those in front-end or PM roles, the HTML/CSS resume is a "live" demonstration of skill. By providing a URL to a responsive resume that maintains perfect rectangularity on the recruiter's specific device, the candidate demonstrates an understanding of modern web standards and user experience. Furthermore, the use of semantic HTML5 tags (\<section\>, \<article\>, \<time\>) provides the cleanest possible data structure for 2026 AI parsers.3

### **The Role of LaTeX in High-Finance and Research**

In quantitative finance and academic-heavy tech roles, LaTeX remains the status quo. Its ability to handle complex mathematical notation alongside pixel-perfect rectangular blocks makes it the "gold standard" for PDFs. The vector-based nature of LaTeX ensure that even if a recruiter prints the resume on a 1200 DPI laser printer, the lines remain sharp and the block edges remain perfectly vertical.26

## **Advanced Accessibility: WCAG and the Fluid Resume**

A "Rectangular Block" resume must not sacrifice accessibility for aesthetics. The 2026 standards for professional documents emphasize that all text must be readable by screen readers and resizable by users with visual impairments.

### **WCAG 1.4.4: Resize Text**

This success criterion requires that text can be resized up to 200% without loss of content or functionality. In a rectangular block resume, this presents a challenge: if the user zooms in, does the block remain a single line, or does it wrap? The "fluid" approach using clamp() and cqi solves this by scaling the text _down_ as the container "narrows" due to zoom, keeping the text on one line for as long as possible.15

### **Semantic Labeling and ARIA Roles**

For the HTML/CSS resume, the use of ARIA (Accessible Rich Internet Applications) labels is critical. While the visual goal is a "block," the structural goal is a "list."

HTML

\<ul role\="list" aria-label\="Professional Experience"\>  
 \<li role\="listitem"\>Led a 10-person engineering team...\</li\>  
\</ul\>

This ensures that while the recruiter sees a beautiful, solid block of text, a blind recruiter's screen reader identifies the information as a structured list of achievements.14

## **Common Pitfalls: Why "Perfect" Blocks Fail**

Even with perfect code, external factors can ruin the rectangular block. Document engineers must account for these variables during the validation phase.

1. **Missing Fonts:** If a recruiter's system lacks Calibri, the browser or PDF viewer will substitute a font like Arial. Because Arial has wider metrics, a line that was "perfect" in Calibri will wrap to a second line.
   - _Remedy:_ Always embed fonts in PDFs and use @font-face for web resumes.5
2. **Printer Margin Scaling:** When printing a PDF, "Fit to Page" settings can alter the scale of the document by 2-5%, potentially introducing line jitter.
   - _Remedy:_ Use 1-inch margins (standard) rather than 0.5-inch margins to provide a safety buffer for physical printers.12
3. **OS Hinting Differences:** Windows (DirectWrite) and macOS (CoreText) render Calibri differently. Windows tends to "snap" glyphs to the pixel grid, while macOS prioritizes the font's organic shape.
   - _Remedy:_ Test the HTML/CSS resume on both platforms using a service like BrowserStack to ensure the text-align-last behavior is consistent.7

## **Validation and Testing Suites**

Before deployment, a rectangular block resume must pass a series of rigorous tests.

- **DPI Stress Test:** View the document at 100%, 125%, 150%, and 200% OS scaling. The blocks should remain solid.
- **Viewport Stress Test:** Use Chrome DevTools to simulate screen widths from 320px (iPhone SE) to 2560px (1440p Monitor).
- **ATS Parser Test:** Paste the text into a plain-text editor (like Notepad). If the text appears jumbled or the bullet points are merged, the layout is too complex for 2026 AI scanners.2
- **Lighthouse Accessibility Audit:** For web resumes, ensure a score of 100 in the accessibility category, confirming that the "block" styling doesn't interfere with readability.14

## **The Convergence of Aesthetics and Analytics**

The "Ultimate Guide to Rectangular Block Resumes" demonstrates that the highest level of professional presentation is achieved through a combination of typographic science and technical engineering. By treating the resume as a responsive application rather than a static document, candidates—especially those in fintech and technology—can project a level of competence that begins before the interview even starts. Whether utilizing the fluid scaling of CSS clamp, the mathematical precision of LaTeX leaders, or the automated consistency of Word VBA, the "rectangular block" is the definitive format for the 2026 professional, ensuring that every bullet point is not just a sentence, but a perfectly engineered achievement.1

#### **Works cited**

1. Best ATS-Friendly Resume Templates, Trends & Formats for 2026, accessed March 4, 2026, [https://resumeoptimizerpro.com/blog/best-ats-friendly-resume-templates-2026](https://resumeoptimizerpro.com/blog/best-ats-friendly-resume-templates-2026)
2. ATS Resume Format That Actually Works in 2026 \- Scale.jobs, accessed March 4, 2026, [https://scale.jobs/blog/ats-resume-format-works-2026](https://scale.jobs/blog/ats-resume-format-works-2026)
3. 5 Resume Formats That Will Dominate 2026 (And 3 That Are Now Obsolete), accessed March 4, 2026, [https://blog.theinterviewguys.com/resume-formats-that-will-dominate-2026/](https://blog.theinterviewguys.com/resume-formats-that-will-dominate-2026/)
4. Calibri Corbel Candara cambria \- Microsoft Learn, accessed March 4, 2026, [https://learn.microsoft.com/en-us/typography/cleartype/pdfs/typesamples.pdf](https://learn.microsoft.com/en-us/typography/cleartype/pdfs/typesamples.pdf)
5. Calibri font family \- Typography | Microsoft Learn, accessed March 4, 2026, [https://learn.microsoft.com/en-us/typography/font-list/calibri](https://learn.microsoft.com/en-us/typography/font-list/calibri)
6. Going in depth on Font Metrics. \- Wolthera.info, accessed March 4, 2026, [https://wolthera.info/2025/04/going-in-depth-on-font-metrics/](https://wolthera.info/2025/04/going-in-depth-on-font-metrics/)
7. Fonts and text metrics \- Win32 apps | Microsoft Learn, accessed March 4, 2026, [https://learn.microsoft.com/en-us/windows/win32/menurc/fonts-and-font-metrics](https://learn.microsoft.com/en-us/windows/win32/menurc/fonts-and-font-metrics)
8. Cell Dimensions \- GitHub, accessed March 4, 2026, [https://github.com/ClosedXML/ClosedXML/wiki/Cell-Dimensions/4876879724ef5784b57451186301294e7616612b](https://github.com/ClosedXML/ClosedXML/wiki/Cell-Dimensions/4876879724ef5784b57451186301294e7616612b)
9. Font Point Size and the Em Square: Not What People Think \- Phinney on Fonts, accessed March 4, 2026, [https://www.thomasphinney.com/2011/03/point-size/](https://www.thomasphinney.com/2011/03/point-size/)
10. PDF: How to know total width of Character including advance width \- Stack Overflow, accessed March 4, 2026, [https://stackoverflow.com/questions/34516699/pdf-how-to-know-total-width-of-character-including-advance-width](https://stackoverflow.com/questions/34516699/pdf-how-to-know-total-width-of-character-including-advance-width)
11. How to measure the pixel width of a digit in a given font / size (C\#) \- Stack Overflow, accessed March 4, 2026, [https://stackoverflow.com/questions/1833062/how-to-measure-the-pixel-width-of-a-digit-in-a-given-font-size-c](https://stackoverflow.com/questions/1833062/how-to-measure-the-pixel-width-of-a-digit-in-a-given-font-size-c)
12. The best resume fonts, sizes, and formatting tips (2026) | Microsoft Word Blog, accessed March 4, 2026, [https://word.cloud.microsoft/create/en/blog/best-resume-fonts/](https://word.cloud.microsoft/create/en/blog/best-resume-fonts/)
13. Character design standards \- Space characters for Latin 1 \- Typography \- Microsoft Learn, accessed March 4, 2026, [https://learn.microsoft.com/en-us/typography/develop/character-design-standards/whitespace](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/whitespace)
14. Container queries, responsive grids, and fluid typography \- Morgan Feeney, accessed March 4, 2026, [https://morganfeeney.com/guides/container-queries/container-queries-responsive-grids-fluid-typography](https://morganfeeney.com/guides/container-queries/container-queries-responsive-grids-fluid-typography)
15. Container Query Units and Fluid Typography | Modern CSS Solutions, accessed March 4, 2026, [https://moderncss.dev/container-query-units-and-fluid-typography/](https://moderncss.dev/container-query-units-and-fluid-typography/)
16. ATS Resume Format 2026: Step-by-Step Guide \- Free Template \- Intelligent CV, accessed March 4, 2026, [https://www.intelligentcv.app/career/ats-resume-format-guide/](https://www.intelligentcv.app/career/ats-resume-format-guide/)
17. 8 Crucial ATS Friendly Resume Tips for US Job Seekers in 2026 \- CV Anywhere, accessed March 4, 2026, [https://cvanywhere.com/blog/ats-friendly-resume-tips](https://cvanywhere.com/blog/ats-friendly-resume-tips)
18. Best Resume Formats for ATS Compatibility in 2026 | PitchMeAI, accessed March 4, 2026, [https://pitchmeai.com/blog/ats-compatible-resume-formats](https://pitchmeai.com/blog/ats-compatible-resume-formats)
19. The Best Resume Format for 2026 (Templates & Examples), accessed March 4, 2026, [https://resumegenius.com/blog/resume-help/resume-format](https://resumegenius.com/blog/resume-help/resume-format)
20. clamp() \- CSS \- MDN Web Docs, accessed March 4, 2026, [https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp)
21. ATS-Friendly Fonts for Your Resume: 2026 Guide \+ Examples \- Enhancv, accessed March 4, 2026, [https://enhancv.com/blog/ats-friendly-fonts/](https://enhancv.com/blog/ats-friendly-fonts/)
22. Responsive fonts using css clamp() | by Matt Claffey \- Medium, accessed March 4, 2026, [https://mattclaffey.medium.com/responsive-fonts-using-css-clamp-26d3d50cdec3](https://mattclaffey.medium.com/responsive-fonts-using-css-clamp-26d3d50cdec3)
23. How to Justify a Single Line of Text in CSS \- Zenn, accessed March 4, 2026, [https://zenn.dev/yend724/articles/20221105-osx4fnh0l44mn3ii?locale=en](https://zenn.dev/yend724/articles/20221105-osx4fnh0l44mn3ii?locale=en)
24. clamp() \- CSS | MDN, accessed March 4, 2026, [https://developer.mozilla.org/en-us/docs/Web/CSS/Reference/Values/clamp](https://developer.mozilla.org/en-us/docs/Web/CSS/Reference/Values/clamp)
25. itemize \- Resume Bullet Point Alignment \- TeX \- LaTeX Stack ..., accessed March 4, 2026, [https://tex.stackexchange.com/questions/327451/resume-bullet-point-alignment](https://tex.stackexchange.com/questions/327451/resume-bullet-point-alignment)
26. Align text to the bullets of a list \- TeX \- LaTeX Stack Exchange, accessed March 4, 2026, [https://tex.stackexchange.com/questions/531108/align-text-to-the-bullets-of-a-list](https://tex.stackexchange.com/questions/531108/align-text-to-the-bullets-of-a-list)
27. hfill \- How to draw a rectangle filling the page after some text? \- TeX ..., accessed March 4, 2026, [https://tex.stackexchange.com/questions/636867/how-to-draw-a-rectangle-filling-the-page-after-some-text](https://tex.stackexchange.com/questions/636867/how-to-draw-a-rectangle-filling-the-page-after-some-text)
28. Line breaks and blank spaces \- Overleaf, Online LaTeX Editor, accessed March 4, 2026, [https://www.overleaf.com/learn/latex/Line_breaks_and_blank_spaces](https://www.overleaf.com/learn/latex/Line_breaks_and_blank_spaces)
29. VBA/Word add bullets, numbering etc \- Stack Overflow, accessed March 4, 2026, [https://stackoverflow.com/questions/23456699/vba-word-add-bullets-numbering-etc](https://stackoverflow.com/questions/23456699/vba-word-add-bullets-numbering-etc)
30. Word VBA line length constraint \- Stack Overflow, accessed March 4, 2026, [https://stackoverflow.com/questions/18923024/word-vba-line-length-constraint](https://stackoverflow.com/questions/18923024/word-vba-line-length-constraint)
31. Change the spaces between text \- Microsoft Support, accessed March 4, 2026, [https://support.microsoft.com/en-us/office/change-the-spaces-between-text-e9b96011-1c42-45c0-ad8f-e8a6e4a33462](https://support.microsoft.com/en-us/office/change-the-spaces-between-text-e9b96011-1c42-45c0-ad8f-e8a6e4a33462)
32. Changing character spacing on all characters next to \* symbol in Word \[word\] : r/vba \- Reddit, accessed March 4, 2026, [https://www.reddit.com/r/vba/comments/s6k0ri/changing_character_spacing_on_all_characters_next/](https://www.reddit.com/r/vba/comments/s6k0ri/changing_character_spacing_on_all_characters_next/)
33. Count Number of Each Character in Word Document \- DocTools, accessed March 4, 2026, [https://www.thedoctools.com/word-macros-tips/word-macros/count-number-of-each-character-in-word-document/](https://www.thedoctools.com/word-macros-tips/word-macros/count-number-of-each-character-in-word-document/)
34. How to change the character spacing in Microsoft Word \- Login, accessed March 4, 2026, [https://www.simuldocs.com/blog/how-to-change-the-character-spacing-in-microsoft-word](https://www.simuldocs.com/blog/how-to-change-the-character-spacing-in-microsoft-word)
35. The Best Resume Fonts and Formatting Choices for 2026, accessed March 4, 2026, [https://www.yeswriting.com/best-resume-fonts-formatting/](https://www.yeswriting.com/best-resume-fonts-formatting/)

[image1]: data:image/png;base64,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ERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERKfg/0UKFmC9sEr4AAAAASUVORK5CYII=
[image2]: data:image/png;base64,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

**Additional Inputs**

To achieve a "zero-wrap, zero-hang" rectangular block while keeping your font size constant, you need to manage your **Character Budget**. Since your table column (`.c4`) is exactly **28.2%** of the page width, your target for a 10pt font is a very narrow window: **38 to 44 characters.**

Here is the professional workflow to "engineer" your bullets using your specific HTML structure:

### Phase 1: The "95% Rule" (Manual Rephrasing)

You should rewrite your bullet points until they look like they almost touch the edge but have 1–3 characters of "air" left.

**PM/Tech Rephrasing Cheat Sheet:**

- **To Add Length (Expand):**
- Change "Led" to "Spearheaded" or "Orchestrated."
- Change "Built" to "Architected and deployed."
- Add context: Change "Reduced TRT 50%" to "Reduced end-to-end TRT by 50%."

- **To Reduce Length (Shrink):**
- Use symbols: Change "percent" to "%" and "dollars" to "$."
- Cut "filler": Remove "the," "a," and "successfully."
- Example: "Led the launch of..." $\rightarrow$ "Launched..."

### Phase 2: The "5% Stretch" (Justification Code)

Once your text is at 95% width, do not add regular spaces (the computer will just ignore them). Instead, use the **Auto-Snap** code for your `.dsc` class:

```css
.dsc li {
  text-align: justify;
  text-align-last: justify; /* Forces the 95% line to snap to 100% */
  white-space: nowrap; /* Safety: Never allows a 2nd line */
}
```

**Why this works:** `text-align-last: justify` takes that tiny bit of remaining "air" and distributes it equally between every word. Because your text is already 95% of the way there, the gaps will be invisible to the human eye, creating a "solid block" effect.

### Phase 3: The "Metric Padding" Trick

If you have a bullet that is _just_ too short and the justification looks "gappy," use **Non-Breaking Spaces** (`&nbsp;`) around your most important numbers (metrics). This is what you meant by "increasing spaces around metrics."

**Instead of writing:**
`<li>Reduced TRT 50% using GenAI</li>` (32 chars - TOO SHORT)

**Write this:**
`<li>Reduced&nbsp;&nbsp;TRT&nbsp;&nbsp;<b>50%</b>&nbsp;&nbsp;via Agentic GenAI</li>` (42 chars - PERFECT)

- **Tip:** `&nbsp;` counts as a character but prevents the computer from putting a line break there. It allows you to manually "push" words toward the right margin.

### Phase 4: How to measure precisely?

To know exactly how close you are to the 95% threshold without guessing, use a "Character Counter" set to your specific limit.

1. **Find your "Master Bullet":** Find one bullet point in your resume that currently looks _perfect_ to you.
2. **Count its characters:** Copy it into a character counter. Let's say it is 42 characters.
3. **Set the Budget:** Every other bullet in that column must now be between **40 and 43 characters.**

### Summary for your HTML file:

- **Target:** 38–44 characters per line for column `.c4`.
- **CSS:** Keep `text-align-last: justify` on all `li` tags.
- **Manual:** If a line is at 35 characters, add one "impact word" (like "streamlined" instead of "led") to reach 40.
- **Final Touch:** Use `<b>` tags on your numbers. Bold characters in Calibri are slightly wider than regular ones, which helps "fill" the line without adding more words.
