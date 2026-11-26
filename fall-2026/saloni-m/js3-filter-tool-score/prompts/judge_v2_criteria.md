You are helping a job seeker decide which postings are worth her time.

The job seeker (fictional persona, no contact details):

{{PERSONA_JSON}}

The posting:

{{POSTING_JSON}}

Is this posting worth her time to read closely and consider applying to? Count it as worth her
time only if all three hold:

1. The job is hands-on building: engineering in ML, AI applications, or data. Customer-facing
   pre-sales, architecture-for-clients, research science, IT and security operations are not.
2. Its stated requirements are within reach: no more than roughly 3 years required, no PhD
   required, and her stack covers a real part of what it asks for.
3. It is not a senior, staff, lead, principal or manager role, whatever the title says.

Location and visa sponsorship do not count. If the posting does not give you enough to decide,
say so.

Reply with only this JSON object and nothing else:

{"verdict": "worth_time" | "not_worth_time" | "cannot_tell", "reason": "one or two sentences"}
