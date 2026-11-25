# Changes pending for FILTER.md v1.1

**Status after FILTER.md v1.1 (2026-11-22, `5dff01f`):** item 1 adopted (growth, revenue and customers dropped), and
the splitter now keeps "U.S.", "e.g." and "i.e." inside a sentence; items 3, 5 and 6 are written into v1.1; items 2
and 4 are left out, since neither fired on any of the 1,509 postings. The text below is kept as it was found.

Found by Claude Code while building and running FILTER.md v1.0 (2026-11-20 and 21). FILTER.md v1.0 itself is not
edited: version 1.0 stays as committed in 66e26d9, and each item below waits for a dated v1.1 entry. The engine
implements v1.0 exactly as written, including the parts flagged here. Every count comes from the filter run
`js3/filter-run/2026-11-21T044414Z/` (1,509 postings, the newest saved answer of each board).

## 1. Section 6, item 3: the R7 company words misfire on real requirements (Claude Code's choice)

Section 6 counts a years sentence as being about the company when it contains grew, grown, growth, founded,
revenue, customers or history, and makes it "cannot tell" instead of a requirement when it asks more than the
person's years. In the run, those words fired 77 times in 72 postings (47 distinct sentences): **growth 56,
customers 12, revenue 9; grew, grown, founded and history 0.** Every one of the 47 sentences is a requirement for
the candidate ("Have 8+ years of experience ... ideally within high-growth tech startups"), not a sentence about
the company. No sentence about the company's own history matched. All 72 postings were rejected by another rule
(R2 for 30, R3 for 25, R4 for 17), so the misfire changed no kept posting and no score in this run; on a posting that passes every other rule it
would keep an 8-year requirement with only 10 points off.

**Proposed for v1.1:** drop growth, revenue and customers from the company words (keep grew, grown, founded and
history), or count a company word only in a sentence whose subject is the company (we, our, the company). The
audit's hand verdicts should decide which.

The 47 sentences (the posting count is how many postings repeat the sentence):

**growth** (34 distinct sentences):

- "- Have 8+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments." (13 postings, e.g. AI Support Engineer - San Francisco)
- "- 10+ years of experience in lifecycle, CRM, retention, growth, product marketing, or marketing technology, ideally in a global B2B business serving self serve small businesses, enterprises, and developers." (1 posting, e.g. Growth - Lifecycle Lead (B2B))
- "- 7–10+ years of HR experience, including at least 5 years as an HR Business Partner in a high-growth or complex environment." (4 postings, e.g. HRBP, Strategy, Finance, and People)
- "- Bring 4–7 years of experience in growth marketing, web strategy, organic acquisition, conversion optimization, or product growth, with measurable acquisition, activation, or revenue impact." (1 posting, e.g. Growth Marketing Manager - Web & Organic, SMB Ads)
- "- 8+ years of B2B growth, demand generation, or performance marketing experience, ideally in high-growth technology or subscription businesses." (1 posting, e.g. Growth - Digital Marketing (Business))
- "- 10+ years of B2B growth, demand generation, or performance marketing experience, including meaningful ownership of enterprise programs." (1 posting, e.g. Growth - Digital Marketing (Enterprise))
- "- Have 10+ years of experience in product marketing, growth, or monetization, including substantial experience with subscriptions." (1 posting, e.g. Growth Product Marketing Manager)
- "- 5+ years of experience in data science or growth analytics within an ads platform, marketplace, or high-growth B2B environment." (1 posting, e.g. Data Scientist, SMB Ads Growth)
- "- Have 5+ years of experience in User Operations, Engineering, Support Engineering or similar technical roles, ideally within high-growth tech startups or other fast-paced environments." (1 posting, e.g. AI Support Engineer - Toronto)
- "- Have 10 years + of experience in growth, strategy, business operations or quantitative analytics with meaningful responsibility for outcomes." (2 postings, e.g. Strategy & Operations Lead, France)
- "- Have 12+ years of experience in B2B marketing or go-to-market leadership, including building programs that drive SMB adoption and growth at a technology, SaaS, or AI company." (1 posting, e.g. Portfolio Product Marketing Lead)
- "- 7+ years of marketing experience, with a strong track record of delivering high-impact consumer campaigns and measurable user or usage growth in Japan." (1 posting, e.g. Consumer Marketing Manager, Japan)
- "- Bring approximately 8-10 years of experience in business incubation, growth, strategy, business operations, product strategy, or consulting, with substantial ownership of implementation and commercial results." (1 posting, e.g. SMB Innovation Sales & Strategy Lead)
- "- 8+ years of progressive recruiting experience in high-growth, premier tech environments" (1 posting, e.g. Technical Recruiter)
- "- 10+ years in SEO or growth marketing, with a track record of growing qualified organic acquisition for B2B software or products serving small businesses." (1 posting, e.g. Growth Marketing Manager, B2B SEO & AEO)
- "Typically 7–10+ years in HR, including at least five years supporting managers and teams in high-growth, international or complex organisations." (4 postings, e.g. Senior HR Business Partner)
- "- 10+ years of experience across product growth, growth marketing, data science, or growth strategy and operations, with hands-on execution in a fast-moving technology company." (2 postings, e.g. Growth Lead, Brazil)
- "- 7+ years of full-cycle recruiting experience, ideally in-house at high-growth or high-bar environments." (1 posting, e.g. Business Recruiter, APAC)
- "- Have 5+ years of experience in compensation operations, HR operations/systems, or total rewards tooling in high-growth or technology environments." (1 posting, e.g. Compensation Operations Analyst)
- "- 8+ years of experience in partner management, product partnerships, strategic partnerships or business development in technology, including ownership of complex partnerships through launch, ongoing growth, expansion and renewal." (1 posting, e.g. Strategic Partnerships Manager, Korea)
- "- 8-10 years of SMB/B2B Self Serve experience in product marketing, growth marketing, lifecycle marketing, consumer marketing, or a related role; equivalent project experience is welcome." (1 posting, e.g. Growth Product Marketing Manager, SMB & B2B Self-Serve)
- "- 5-7+ years of full-cycle recruiting experience, ideally in-house at high-growth or high-bar environments." (2 postings, e.g. Business Recruiter)
- "- Have 6+ years of product management experience, including a track record of delivering measurable growth for self-serve SaaS, business, or team-based products." (1 posting, e.g. Product Manager, ChatGPT Business Growth)
- "The ideal candidate brings 10–15 years of policy experience, strong relationship-building capabilities, and a proven track record of connecting policy strategy directly to business growth." (1 posting, e.g. Director/Senior Manager, Government Affairs)
- "5+ years of experience in growth marketing, lifecycle marketing, growth product, biz ops, a startup or equivalent." (1 posting, e.g. Growth Marketing Manager, Organic & Conversion)
- "4+ years of experience in growth marketing, performance marketing, paid media, marketing science, a startup or equivalent." (1 posting, e.g. Growth Marketing Manager, Upper Funnel)
- "5+ years of experience in analytics, strategy, consulting, growth, or a related field." (1 posting, e.g. Growth Strategy & Analytics Manager)
- "8–12+ years of security operations experience, including at least 4 years leading teams or vendor workforces in a corporate, high-growth tech or similar environment" (2 postings, e.g. Physical Security Operations, Senior Manager)
- "6-10 years of experience in driving revenue growth through product marketing, go-to-market strategy, or another analytical and commercially-oriented role" (1 posting, e.g. Product Growth Manager, Access Control)
- "Minimum 5+ years of direct sales management experience leading AE Enterprise teams at a hyper-growth SaaS B2B, Infrastructure company or Tech company" (1 posting, e.g. Regional Sales Manager, LATAM)
- "7+ years of experience in growth marketing, lifecycle marketing, growth product, biz ops, a startup or equivalent." (1 posting, e.g. Senior Growth Marketing Manager, Organic and Conversion)
- "7+ years of experience in growth marketing, performance marketing, paid media, marketing science, a startup or equivalent." (1 posting, e.g. Senior Growth Marketing Manager, Upper Funnel)
- "6+ years of HRBP or People Business Partner experience, ideally supporting high-growth GTM or Sales organizations" (1 posting, e.g. Senior People Business Partner, Sales)
- "Experience: 4+ years of professional experience in program management, program administration, or early career/university recruiting within a high-growth environment." (1 posting, e.g. Verkademy Program Coordinator)

**customers** (8 distinct sentences):

- "- Bring 7+ years of hands-on technical experience in cybersecurity, cyber operations, or security-focused software engineering, including work directly with government customers or national security mission teams." (1 posting, e.g. Applied AI Engineer, Cyber, Government)
- "- Have 5+ years of technical consulting, post-sales engineering, solutions architecture, or similar experience working directly with customers." (3 postings, e.g. Applied AI Engineer, Codex)
- "- Bring 8+ years of deep, hands-on technical experience and an eagerness to work closely with customers." (3 postings, e.g. Applied AI Engineer, API Platform, Digital Natives)
- "- 14+ years selling complex platform-as-a-service and/or software-as-a-service products to large enterprise customers, with substantial experience in cybersecurity." (1 posting, e.g. Account Director, Cyber)
- "- 14+ years selling complex enterprise software, cloud, AI, data, or platform solutions to life sciences customers" (1 posting, e.g. Account Director, Life Sciences)
- "- 10+ years experience managing high-value external relationships (e.g., customers, partners, investors, Board of Directors) and working directly with founders and C-level executives." (1 posting, e.g. VC Partnerships Manager)
- "- Bring 7+ years of technical consulting (or equivalent) experience with public sector customers (U.S." (1 posting, e.g. Applied AI Engineer, Government)
- "- 14+ years selling complex platform-as-a-service and/or software-as-a-service products to large enterprise customers." (1 posting, e.g. Account Director, Large Enterprise)

**revenue** (5 distinct sentences):

- "- 5+ years of experience in vendor operations, commercial operations, outsourced sales, or a scaled revenue organization" (3 postings, e.g. APAC Vendor Lead, Ads - Sydney)
- "- 10+ years of technical revenue accounting or related advisory experience, with deep ASC 606 expertise and experience leading complex workstreams or teams." (1 posting, e.g. Lead Revenue Accounting, Technical (Strategic Partnerships))
- "- 10+ years of experience selling platform-as-a-service and/or software-as-a-service solutions, with a sustained record of meeting or exceeding meaningful revenue targets through complex, multi-year enterprise sales motions." (1 posting, e.g. Account Director, Higher Education)
- "- 10+ years of experience in B2B marketing operations, marketing technology, revenue operations, or a closely related function." (1 posting, e.g. Marketing Technology & Operations Lead, APAC)
- "Five or more years of experience in Marketing Operations, Revenue Operations, Business Systems, Marketing Technology, or a related field." (3 postings, e.g. AI Marketing Engineer)

## 2. Section 6, item 2: a season wholly before the earliest start is "cannot tell", not a rejection

Section 1 (R6) rejects a start that is clearly before May 2027. Section 6, item 2, as written, makes every season or
quarter "cannot tell" unless it lies wholly after May 2027, so "Start in Fall 2026" (clearly before) is "cannot
tell" with 10 points off instead of a rejection. The engine follows v1.0 (a test pins it). The rule fired 0 times in
the run. **Proposed for v1.1:** a season or quarter that lies wholly before the earliest start rejects.

## 3. Section 7: `years_max` is a person fact

`years_max: 3` is Jane's years of experience, not a rule. The engine reads the person's years from the profile
(`experience.full_time_years`), as Section 6, item 8 says person facts come from the profile; a test checks that the
two agree for Jane. **Proposed for v1.1:** drop `years_max` from Section 7, or label it as Jane's value.

## 4. Section 6, item 5: US remote spellings outside the person's three phrases

Section 1 (R2) keeps "US remote" with no penalty, but Section 6, item 5 counts only the person's three remote
phrases (and Lever's remote + US) as US remote, so "Remote (United States)" is another US place, minus 15. It fired
0 times in the run. **Proposed for v1.1:** any location that is in the US and says remote counts as US remote.

## 5. Section 3: posting dates for Greenhouse and Lever

Section 3 lists `publishedAt` among the fields the agent maps for all three systems; before commit 353b67a only
Ashby had it. The reader now maps Greenhouse `first_published` (or `updated_at`) and Lever `createdAt` (written as
UTC), which the tie and duplicate rules need. **Proposed for v1.1:** say where each system's date comes from.

## 6. Sections 2 and 3: a posting with no id, and the order of the rules

FILTER.md does not say what happens to a posting with no id. The reader still treats it as a broken answer (the
board is unverified), because a board's state is kept by posting ids, and an answer in which no posting has a
title is also still unverified. FILTER.md also does not say which failed rule is the deciding one; the engine runs
every rule and names the first failure in the order R1 to R8, as contract v0.2 did. **Proposed for v1.1:** say both.

## 7. Found by the fresh set (2026-11-24): R4's title words, and a cutoff equal to the start score

Added by Claude Code after the fresh set was scored (`js3/fresh/2026-11-22T084738Z/RESULTS.md`, `c01dc04`). Of the 12
postings v1.1 newly recommends, Aravind rejected 2: "Software Engineer - Frontend Developer Productivity" (Palantir;
his note: "Frontend-focused role, outside Jane's main interests") and "Control Systems Software Engineer, Robotics"
(OpenAI; "Specialized robotics and control systems role requiring hardware-focused experience"). R4 passed both
because each title contains "Software Engineer". Both scored 50, the start, with no topic group, so at v1.1's cutoff of
50 the score screened nothing and R4 alone let them through. On the whole v1.1 run, 25 of the 99 kept postings score 50
with no topic group, and each of those two titles is the only kept one with its words ("Frontend"; "Control Systems"
or "Robotics").

**Not proposed; Aravind's call if there is a v1.2.** The options, with what this set shows (development data from the
moment one is chosen from it, so a new set would be needed to test the choice):
- add title words to R4's excludes, such as "Control Systems" and "Frontend": on this run that removes exactly these
  two kept postings;
- a cutoff above the start score, so a posting needs at least one topic group: at 55, v1.1 would agree with him on 6
  of the 12 (it would drop both rejects and 6 of his 10 keeps), against 10 of 12 at 50;
- leave both as they are and accept such keeps: a person reads every shortlisted posting anyway.
