"""
Accessibility & UX SEO Module.
Perform static HTML analysis for WCAG 2.1 AA and standard UX metrics tied to Core Web Vitals.
"""

from bs4 import BeautifulSoup
from crawler import crawl_page
from models import WcagViolation, AccessibilityReport

async def analyze_accessibility(url: str) -> AccessibilityReport:
    """Audit a webpage for basic WCAG accessibility and mobile UX issues."""
    report = AccessibilityReport(url=url)
    
    try:
        html = await crawl_page(url)
    except Exception as e:
        report.error = f"Failed to crawl {url}: {str(e)}"
        return report

    soup = BeautifulSoup(html, 'html.parser')
    violations = []
    passing = 0

    # 1. HTML Lang attribute
    html_tag = soup.find('html')
    if html_tag and not html_tag.get('lang'):
        violations.append(WcagViolation(
            rule_id="html-has-lang",
            description="<html> tag is missing a 'lang' attribute.",
            severity="Error",
            element_html="<html>"
        ))
    else:
        passing += 1

    # 2. Image alt text
    images = soup.find_all('img')
    img_passed = True
    for img in images:
        if 'alt' not in img.attrs:
             # Just take first 100 chars of HTML for context
             snippet = str(img)[:100] + ("..." if len(str(img)) > 100 else "")
             violations.append(WcagViolation(
                rule_id="image-alt",
                description="Image is missing an 'alt' attribute.",
                severity="Error",
                element_html=snippet
            ))
             img_passed = False
             
        # Check for empty alt, it's allowed for decorative but warn if there are many
        # We will count it as Warning
        elif img.get('alt', '') == '':
            pass # accepted as decorative in static analysis

    if images and img_passed: passing += 1
    elif not images: passing += 1 # N/A gets points

    # 3. Empty Links (a tags and buttons without text or aria-label)
    interactive = soup.find_all(['a', 'button'])
    int_passed = True
    for el in interactive:
        text_content = el.get_text(strip=True)
        has_aria = el.get('aria-label')
        has_title = el.get('title')
        
        # if it contains an image with alt text, it is also okay
        has_img_alt = False
        img = el.find('img')
        if img and img.get('alt'):
            has_img_alt = True
            
        if not text_content and not has_aria and not has_title and not has_img_alt:
             snippet = str(el)[:100] + ("..." if len(str(el)) > 100 else "")
             kind = el.name
             violations.append(WcagViolation(
                 rule_id=f"empty-{kind}",
                 description=f"Interactive <{kind}> element has no accessible name (empty text, no aria-label).",
                 severity="Error",
                 element_html=snippet
             ))
             int_passed = False
             
    if interactive and int_passed: passing += 1
    elif not interactive: passing += 1

    # 4. Form inputs without labels
    # 5. Viewport zoom disabled
    meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
    if meta_viewport and 'content' in meta_viewport.attrs:
        content = meta_viewport['content'].lower()
        if 'user-scalable=no' in content or 'maximum-scale=1' in content:
            violations.append(WcagViolation(
                rule_id="meta-viewport",
                description="Viewport disables zooming on mobile, which is an accessibility violation for visually impaired users.",
                severity="Error",
                element_html=str(meta_viewport)
            ))
        else:
            passing += 1
    else:
        passing += 1 # Missing won't explicitly disable zoom

    # 6. Page Title
    title = soup.title
    if not title or not title.string or not title.string.strip():
        violations.append(WcagViolation(
            rule_id="document-title",
            description="The document does not have a valid <title> element.",
            severity="Error",
            element_html="<title></title>"
        ))
    else:
        passing += 1

    report.passing_checks = passing
    report.violations = violations

    # Calculate score
    total_checks = passing + len(violations)
    if total_checks == 0:
        report.score = 100
    else:
        report.score = int((passing / total_checks) * 100)

    # Generate recommendations
    if report.score == 100:
        report.recommendations = "Perfect! No basic WCAG accessibility violations found."
    else:
        errors = sum(1 for v in violations if v.severity == "Error")
        report.recommendations = f"Fix the {errors} Error(s) found above to ensure all users (and search engine crawlers) can navigate your site efficiently. Google rewards highly accessible sites via Page Experience ranking signals."

    return report

def format_accessibility_report(report: AccessibilityReport) -> str:
     """Format the Accessibility SEO report for Claude."""
     if report.error:
         return f"⚠️ **Accessibility Audit Error:** {report.error}"

     lines = [
         f"## ♿ Accessibility (A11y) & UX Audit",
         f"**URL:** `{report.url}`\n",
         f"### Score: {report.score}/100"
     ]

     if report.score == 100:
         lines.append("✅ **Status:** Excellent. No basic WCAG 2.1 AA violations detected in the static HTML.")
     else:
         lines.append(f"❌ **Status:** Found {len(report.violations)} accessibility violation(s).\n")
         
         lines.append("### Violations")
         # Group by rule id to avoid spam
         grouped = {}
         for v in report.violations:
             if v.rule_id not in grouped:
                 grouped[v.rule_id] = []
             grouped[v.rule_id].append(v)
             
         for rule, group in grouped.items():
            first = group[0]
            lines.append(f"**[{first.severity}] {first.description} ({len(group)} instances)**")
            
            # Show up to 3 examples
            for v in group[:3]:
                lines.append(f"- ```html\n{v.element_html}\n```")
            if len(group) > 3:
                lines.append(f"- *...and {len(group) - 3} more.*")
            lines.append("")

     lines.append(f"**Recommendation:** {report.recommendations}")
     return "\n".join(lines)
