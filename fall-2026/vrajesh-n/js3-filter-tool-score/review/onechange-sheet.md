# One-change sheet (blind)
For each posting, read the excerpts and the claim, then judge the two sentences X and Y that Claude wrote. **accurate** = a reader who sees only that sentence would understand correctly what the posting says about the claim (including 'I cannot tell' when the text is silent). **misleading** = the reader would draw a wrong or unsupported conclusion. Write `accurate` or `misleading` for X and Y in `onechange-labels.csv`. You do not know which sentence came from which variant.

## 1. PhD Intern, Software Engineer - Graphics (2027) (greenhouse_figma)
- location: San Francisco, CA • New York, NY
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts: drock role for the company because it underpins the technology driving the user experience, touching many other teams, and as such is one of the most impactful areas of F ... ore! We'd love to hear from you if you have: Current enrollment as a 4th or 5th year senior PhD student pursuing a PhD in Computer Graphics, Media Processing, or a related field Experience working with OpenGL, WebGL, WebGPU, Vulkan or Metal and their respective shader ... k record of rigorous problem-solving through academic or applied research, with experience thinking holistically about use cases and the low-level technology required Whi ... mization, animation, geometry, or media Interest in art and design applications Experience using AI tools (e.g., GitHub Copilot, ChatGPT, Claude) to write, debug, and optimize code Related industry experience via a past internship or full-time role Strong communication and interpersonal skills, with demonstrated experience collaborating across functions At Figma, one of our values is Grow as you go. W ... learn and develop their skills. If you’re excited about this role but your past experience doesn’t align perfectly with the points outlined in the job description, we enc ... and support our differences. We know employing a team rich in diverse thoughts, experiences, and opinions allows our employees, our product and our community to flourish. ... To help candidates focus on the opportunities most relevant to their skills and experience, Figma limits the number and frequency of applications. These limits apply to a
- **X:** I cannot tell: the posting text gives no years of experience, so the tool labeled the 'early_career' claim "insufficient" and neither supports nor contradicts it.
- **Y:** I cannot tell: the posting's text states no years of experience, so the tool labeled the early_career claim (that it asks for fewer than 3 years) "insufficient", which means the text neither supports nor contradicts it.

## 2. Software Engineer, Full Stack - Experimentation Platform (greenhouse_doordashusa)
- location: San Francisco, CA; Sunnyvale, CA; Seattle, WA; New York, NY; Los Angeles, CA
- **claim:** The posting names a technology from Rohan's documented shipped project (Go, PostgreSQL, Terraform, GraphQL, DigitalOcean).
- excerpts: s product experience. Own features end-to-end, from APIs and data models to the React UI in our Decision Portal, context switching between frontend, backend, and dat ... nt. 2+ years of industry experience building web applications end-to-end, using TypeScript with React on the frontend. Exceptionally strong knowledge of CS fundamental concepts and  ... e right kind of storage layers for the problem at hand. Backend experience with Java, Kotlin, Python, or Go. Experience with documentation, unit, integration, and end-to-end testing acros ... re flagging products. Experience with any of the “Big Data” technologies (e.g., Postgres, Redis, Elasticsearch, Snowflake, Mode, Segment, Spark, etc.). Experience in any data- ... stics, machine learning, etc. Familiarity with cloud-based environments such as AWS. Compensation The successful candidate’s starting pay will fall within the pay  ... ling door-to-door delivery, and we are looking for team members who can help us go from a company that is known as the place you order food to a company that peop
- **X:** The posting's text names at least one technology from Rohan's documented shipped project (it lists "Postgres, Redis, Elasticsearch" as example data technologies), so the stack_fit claim is labeled supported, though the match comes from an "e.g." option list and the quoted snippet is cut off, so it is a text match and not proof that the role requires that stack.
- **Y:** The posting's text names data technologies such as Postgres, Redis and Elasticsearch, and the tool labeled "stack_fit" as supported on that basis. However, the quote it gave is cut off mid-word and has no explanation attached, so we can be fairly but not fully sure that the posting's stack matches.

## 3. Forward Deployed Software Engineer, New Grad - Commercial (lever_palantir)
- location: Chicago, IL
- **claim:** The posting names a technology from Rohan's documented shipped project (Go, PostgreSQL, Terraform, GraphQL, DigitalOcean).
- excerpts: , and Data Science. Proficiency with one or more programming languages, such as Python, Java, C++, TypeScript/JavaScript, or similar. Must be graduating in December 2026 or Spring 2027. To apply, plea
- **X:** I cannot tell: the tool labeled "stack_fit" as insufficient for this posting, because no technology from the resume's shipped skills appears as a stated need in the posting's text, so the text gives no evidence either way.
- **Y:** I cannot tell: the posting's text names none of the technologies from the persona's shipped project as a stated need, so the stack_fit claim was labeled "insufficient" with no supporting quote.

## 4. Forward Deployed Software Engineer, Internship - Commercial (lever_palantir)
- location: New York, NY
- **claim:** The posting names a technology from Rohan's documented shipped project (Go, PostgreSQL, Terraform, GraphQL, DigitalOcean).
- excerpts: , and Data Science. Proficiency with one or more programming languages, such as Python, Java, C++, TypeScript/JavaScript, or similar. Must be graduating in December 2027 or Spring 2028. To apply, plea
- **X:** I cannot tell: the posting's text names none of the technologies from the candidate's shipped project as something it needs, so the stack_fit claim is labeled "insufficient" - that says the text gives no evidence either way, not that the stack is a bad fit.
- **Y:** I cannot tell: the posting's text names no technology that the candidate has shipped as a stated need, so the tool labeled "stack_fit" as insufficient, and we can't say whether the stack fits or how sure to be.

## 5. Software Engineer, Backend (All Teams) (greenhouse_doordashusa)
- location: San Francisco, CA; New York City, NY;  Sunnyvale, CA; Seattle, WA
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts: rld's most reliable on-demand, logistics engine for delivery! We're looking for experienced engineers to join our fast-growing engineering team to help us develop a 24x7, ... because you have... B.S., M.S., or PhD. in Computer Science or equivalent Prior experience (2+ years industry experience) working with backend tech stacks Proficiency in using AI coding tools (e.g., C ...  and improve efficiency, scalability, and stability of various system resources Experience with service oriented architecture, writing REST API’s, unit testing, and archi ... ectural design Understanding of modern web stacks and architecture (HTTP, REST) Experience with SQL and NoSQL databases and other technologies (e.g. Postgres, Redis, Elas ...  determined based on job-related factors including, but not limited to, skills, experience, qualifications, work location, and market conditions. Base salary is localized ... ied roles: flexible paid time off/vacation, plus 80 hours of paid sick time per year. For hourly roles: vacation accrued at about 1 hour for every 25.97 hours worke ...  That’s why we hire and cultivate diverse teams of people from all backgrounds, experiences, and perspectives. We believe that true innovation happens when everyone has r
- **X:** The posting asks for "2+ years industry experience" with backend tech stacks, which is under the 3-year cutoff, so the tool labels the early_career claim "supported" and the quoted text backs that up directly, though it only shows what the posting says and not whether a new grad would be hired.
- **Y:** The posting's text is labeled "supported" for early_career, quoting a requirement of "2+ years industry experience" with backend tech stacks, so it appears to fit an early-career applicant, though the label comes from a rules-based check and the quote shows a 2-year experience ask that sits near the edge of what counts as entry-level.

## 6. Software Engineer I (greenhouse_twitch)
- location: San Francisco, CA
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts:  growth, engagement, and revenue for our streamers while delivering exceptional experiences that delight our viewers. Our mission is to design smarter tools, seamless pat ... making sure Web and Mobile Twitch “Just Works” and also evolving the mobile app experience in new and exciting ways. Our consumer facing features span both web and mobile ... hey work. You can work in San Francisco, CA You Will: Deliver high quality user experiences across Web and Mobile surfaces Partner with product managers, designers, and e ...  Minimum of Bachelor’s degree in Computer Science or prior relevant engineering experiences 1+ years of professional engineering experience building consumer-facing products at scale Experience communicating complicated technical problems to both technical and business audiences A track record of thinking through and shipping quality user experiences Enthusiasm for AI driven engineering practices and a continuous desire to opti ...  development lifecycles using modern automated tools. Bonus Points React Native experience Go, or other backend languages we use at Twitch AWS experience (ECS, DynamoDB, Lambda, SQS, Step Functions) Familiarity with Twitch, gaming, a ...  units (RSUs). Final compensation will be determined based on factors including experience, qualifications, and location. Amazon also offers comprehensive benefits includ
- **X:** The posting's text supports the early-career claim, since it asks for only "1+ years of professional engineering experience" (or a Computer Science background) for a "Software Engineer I" role, and the tool labels it "supported" from a quoted excerpt of the posting, so we can be fairly but not perfectly sure.
- **Y:** The posting's text supports the claim that it asks for fewer than 3 years of experience, because it quotes "1+ years of professional engineering experience", so we can be fairly sure, though that rests on one quoted line.

## 7. Solutions Architect - Healthcare/Life Sciences Team (HLS) (greenhouse_databricks)
- location: Remote - Illinois
- **claim:** No security clearance is required.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the posting's text never mentions a security clearance, so the tool labelled the "no_clearance" claim "insufficient" and gave no quote, which means we can't be sure either way.
- **Y:** I cannot tell: the posting's text never mentions a security clearance, so the 'no_clearance' claim is labeled "insufficient", meaning it is neither confirmed nor contradicted and there is no quoted evidence to rely on.

## 8. Software Engineer I (greenhouse_twitch)
- location: San Francisco, CA
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts:  growth, engagement, and revenue for our streamers while delivering exceptional experiences that delight our viewers. Our mission is to make Twitch a place viewers return ... ir favorite Creators, spanning both web and mobile surfaces. Which part of that experience we focus on changes often, but some of the spaces we own include Channel Points ...  leads, and other engineers to design, develop, launch, and operate interactive experiences and products Work backwards from customer problems to drive business impactMai ... g backend services Maintain and improve our existing backend services You Have: Experience developing software in a professional environment Prior experience building consumer-facing products at scale Proficient coding skills in modern l ... Objective-C etc Proven ability with thinking though and delivering quality user experiences. Minimum of Bachelor’s degree in Computer Science or equivalent experience Bonus Points Experience with languages/frameworks we use at Twitch: React, Typescript, Golang Experience building software and services using AWS technologies such as ECS, DynamoDB, La ...  units (RSUs). Final compensation will be determined based on factors including experience, qualifications, and location. Amazon also offers comprehensive benefits includ
- **X:** I cannot tell: the tool labeled the 'early_career' claim "insufficient" for this posting (Twitch's Software Engineer I) because the text states no years of experience, so it gave no quote either way and we can't be sure of anything on that claim.
- **Y:** I cannot tell: the tool labeled the 'early_career' claim (that the posting asks for fewer than 3 years of experience) as "insufficient", because the posting's text states no years of experience, so the label gives us nothing to be sure about.

## 9. Backend Engineer, Link (greenhouse_stripe)
- location: NYC, Sea, SF, Tor
- **claim:** The employer will sponsor a visa.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the posting's text says nothing about sponsoring visas, so the tool labeled the sponsorship claim "insufficient", and the text gives no evidence either way.
- **Y:** I cannot tell: the posting's text says nothing about sponsoring visas, so the tool labeled the sponsorship claim "insufficient" and the posting gives no basis for either answer.

## 10. Software Engineer, Scribe AI (ashby_commure)
- location: Mountain View, CA
- **claim:** The work involves building with LLMs or AI agents.
- excerpts: At Commure, we're building the AI Operating System for healthcare, the foundation that defines how care is delive ... ed, documented, and financed. Our platform spans the full care journey: Ambient AI and Dictation eliminating documentation burden at the point of care, intelligent Agents automating patient and revenue workflows, and autonomous RCM processing billions in claims, all on a single AI-native platform integrated with 60+ EHRs. Healthcare carries a $1 trillion a ...  this mission. We've also been named to the Fortune Future 50 list and the 2026 AI Breakthrough Awards for “Overall NLP Company of the Year.” Our team works di ... vel to meet customers. What You'll Do - Develop and scale features for our AI medical scribe, using cutting-edge LLM models to create accurate, structured clinical notes. - Build polished, respo
- **X:** The posting's own text says the work involves building with LLMs, since it describes scaling features for an AI medical scribe "using cutting-edge LLM models to create accurate, structured clinical notes", and the tool labeled this claim "supported" with that direct quote, so we can be fairly confident, though this is only what the posting says and not proof of the actual day-to-day work.
- **Y:** The posting's text supports the claim that the role is AI-focused, because it describes building features for an "AI medical scribe" that uses LLM models to write clinical notes. That is a direct quote from the posting, so we can be fairly sure, though the tool only checks what the text says and not how much of the job is actually AI work.

## 11. Fullstack Engineer, Ambient AI (ashby_commure)
- location: Mountain View, CA
- **claim:** The work involves building with LLMs or AI agents.
- excerpts: At Commure, we're building the AI Operating System for healthcare, the foundation that defines how care is delive ... ed, documented, and financed. Our platform spans the full care journey: Ambient AI and Dictation eliminating documentation burden at the point of care, intelligent Agents automating patient and revenue workflows, and autonomous RCM processing billions in claims, all on a single AI-native platform integrated with 60+ EHRs. Healthcare carries a $1 trillion a ...  this mission. We've also been named to the Fortune Future 50 list and the 2026 AI Breakthrough Awards for “Overall NLP Company of the Year.” Our team works di ... his transformation. About the Role We’re building a next-generation ambient AI platform for healthcare, helping clinicians focus on patient care by automatica ... ross the full care workflow, from capturing patient conversations and reviewing AI-generated documentation to coordinating follow-up actions and completing work a ... You’ll work across our mobile and web applications, backend services, APIs, and AI-powered workflows, partnering closely with product, design, clinical, and AI teams. This role is for an engineer who cares deeply about the people using th ... fining an interaction, designing an API, improving a data model, integrating an AI capability, or strengthening the system behind the experience. Our mobile appl ... ation through launch, measurement, and iteration. - Develop new workflows for AI-native healthcare software, including: - Real-time transcription and ambient documentation - AI-assisted review, editing, and clinical 
- **X:** The posting's text supports the claim that the role is AI-focused, since it describes multimodal inputs, intelligent recommendations and agentic actions that help clinicians complete work, and the tool gave this a "supported" label backed by a direct quote, though that quote is a truncated excerpt, so the confidence rests on that one passage alone.
- **Y:** The posting's text supports the claim that the work involves building with LLMs or AI agents, because it quotes "Agentic actions that help clinicians complete work" and "intelligent recommendations", and since the tool labeled this "supported" with a direct quote, we can be fairly confident, though only as far as that one quoted passage goes.

## 12. Forward Deployed Software Engineer, Internship - Warp Speed (lever_palantir)
- location: New York, NY
- **claim:** The role is in the US.
- excerpts: your personal data will be processed by Palantir, please see our Privacy Policy.
- **X:** The posting's text gives its location as "New York, NY", so the tool labeled the US-location claim "supported". That label rests on one direct quote, but it only tells us the listed location is in the US, and it says nothing about whether the role allows remote work or has other location conditions.
- **Y:** The posting's location field reads "New York, NY", which supports the claim that the role is in the US, and we can be fairly confident in that because the tool labeled it "supported" based on a direct quote from the posting, though that only covers what the listing text says.

## 13. Solutions Architect - Manufacturing (greenhouse_databricks)
- location: Chicago, Illinois
- **claim:** No security clearance is required.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the tool labelled the 'no_clearance' claim "insufficient" because the posting's text never mentions a security clearance, so it neither supports nor contradicts the claim, and the tool gave no quote to back either reading.
- **Y:** I cannot tell: the posting's text never mentions a security clearance, so the tool labeled the "no clearance required" claim "insufficient", meaning the text gives no evidence for or against it.

## 14. Software Engineer, New Grad - Query Engines (lever_palantir)
- location: New York, NY
- **claim:** The employer will sponsor a visa.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the posting's text says nothing about sponsoring visas, so the "sponsorship" claim is labeled insufficient, meaning there is no evidence either way and nothing to be sure of.
- **Y:** I cannot tell: the posting's text says nothing about visa sponsorship, so the tool labeled the sponsorship claim "insufficient" and gave no quote, which means we can't be sure either way.

## 15. Backend/API Engineer, Money as a Service (greenhouse_stripe)
- location: US
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts: l stages. Please note we may also consider you for different orgs based on your experience, location, etc. Find more information on our team matching process here. What y ... erred qualifications are a bonus, not a requirement. Minimum requirements 2–12+ years of industry software engineering experience (does not include internships or co-ops) Strong coding skills in any programmin ...  problems and delight both internal and external users Preferred qualifications Experience with large-scale financial tracking systems Good understanding and practical kn
- **X:** The tool labels the early-career claim "supported" because the posting's minimum requirements say "2–12+ years of industry software engineering experience", whose low end is under 3 years. But that range reaches 12 or more years, so I'm only moderately sure, since the lower bound may be for a different level of the same role.
- **Y:** The tool labelled "early_career" as supported, but the only text it quoted as evidence says the minimum requirement is "2-12+ years of industry software engineering experience", which points away from an entry-level role, so I would not trust that label without reading the posting itself.

## 16. Software Engineer - Frontend Developer Productivity (lever_palantir)
- location: New York, NY
- **claim:** The posting names a technology from Rohan's documented shipped project (Go, PostgreSQL, Terraform, GraphQL, DigitalOcean).
- excerpts: ntends, including feature flags, internationalization, and commit previews. • A GraphQL API for declarative data loading, spanning many underlying services. • Blueprin ... l tech talks. Technologies We Use A variety of programming languages, including TypeScript, SCSS, and Java. Open-source libraries and frameworks like React and GraphQL. Industry-standard build tooling, including Gradle, Webpack, CircleCI, and GitH ...  engineering experience. Strong coding skills, with demonstrated proficiency in JavaScript/TypeScript, Java, C++, Python, or another similar programming language. Great problem solving skills with the
- **X:** The posting's text names GraphQL, a technology from Rohan's documented shipped project, so the 'stack_fit' claim is supported by a direct quote, though that only shows the technology is mentioned (not that it is a core requirement) and the tool gave no confidence score beyond the "supported" label.
- **Y:** The posting's text mentions GraphQL, a technology on the candidate's resume, so the label for stack_fit is "supported", but that rests on a single quoted phrase and the tool gave no confidence score or fuller explanation, so we can only say it is a modest, text-based match.

## 17. Software Engineer - Frontend Developer Productivity (lever_palantir)
- location: New York, NY
- **claim:** No security clearance is required.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the tool labelled the 'no_clearance' claim "insufficient" because the posting's text never mentions a security clearance, so nothing in it supports or contradicts the claim, and we can't be sure either way.
- **Y:** The posting's text never mentions a security clearance, so the tool labeled the claim "no clearance is required" as insufficient and I cannot tell whether one is needed, because the tool gives no quote and no confidence level beyond that label.

## 18. Backend/API Engineer, Money as a Service (greenhouse_stripe)
- location: US
- **claim:** The employer will sponsor a visa.
- excerpts: (no matching words anywhere in the text)
- **X:** I cannot tell: the posting's text says nothing about visa sponsorship (the tool labeled the claim "insufficient" and gave no quote), so we have no evidence either way, and no confidence in any answer.
- **Y:** I cannot tell: the posting's text says nothing about sponsoring visas, so the tool labeled the sponsorship claim "insufficient" and we have no evidence either way.

## 19. Backend Engineer, Privy (greenhouse_stripe)
- location: NYC-Privy
- **claim:** The role is in the US.
- excerpts: racting with smart contracts Experience in authentication, identity, or security
- **X:** The posting's location field reads "NYC-Privy", which the tool labeled as supporting a US location, though the label rests on that short location string alone, so we can be fairly but not fully sure it is in the US.
- **Y:** The posting's location field reads "NYC-Privy", which the tool labelled as supporting that the role is in the US. The only evidence is that short location string, so I'd call it fairly but not fully certain.

## 20. Forward Deployed Software Engineer, Internship - US Government (lever_palantir)
- location: Honolulu, HI
- **claim:** The posting asks for fewer than 3 years of experience.
- excerpts:  position will be determined by each individual’s relevant qualifications, work experience, skills, and other factors. This estimate excludes the value of any benefits of
- **X:** I cannot tell: the tool labeled the 'early_career' claim "insufficient" because the posting's text states no years of experience, so we can't be sure either way, even though the title says "Internship."
- **Y:** I cannot tell: the tool labeled the 'early_career' claim (that the posting asks for fewer than 3 years of experience) as insufficient, because the posting's text states no years of experience, so we can't be sure either way.
