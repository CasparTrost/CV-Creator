# -*- coding: utf-8 -*-
"""Page copy for the site.

Guides are dictionaries rather than files so that the table of contents,
the related-reading cards, the sitemap and the schema blocks all come
from one place. Body text is plain HTML; the classes it uses are defined
in assets/site.css.
"""

UPDATED = '2026-09-11'

GUIDES = []


def guide(**kw):
    kw.setdefault('updated', UPDATED)
    GUIDES.append(kw)


# ==================================================================== 1
guide(
    slug='how-to-write-a-resume',
    short='How to write a resume',
    h1='How to write a resume',
    title='How to write a resume: a step-by-step guide with examples',
    description='What goes on a resume, in what order, and how to write each part. '
                'A practical guide with before-and-after examples, no filler.',
    dek='Most resume advice is either a list of adjectives or a sales page. This is the '
        'whole job, start to finish: what to put on the page, in what order, and how to '
        'write the lines that decide whether anyone reads the rest.',
    tag='Starting out',
    minutes=12,
    related=['resume-bullet-points', 'ats-friendly-resume', 'resume-length'],
    faq=[
        ('How long should it take to write a resume?',
         'Two to three hours for the first version if you already have your dates and '
         'job titles to hand. Most of that time goes into the bullet points under your '
         'current job; everything else is transcription.'),
        ('Should I put a photo on my resume?',
         'In the United States, the United Kingdom, Ireland, Canada and Australia, no — '
         'many employers discard resumes with photos to avoid discrimination claims. In '
         'Germany, Austria and Switzerland a photo is still normal, though no longer required.'),
        ('Do I need a different resume for every application?',
         'Not a different resume, but a different top third. Keep one master document and '
         'change the summary, the order of the skills and the three bullet points nearest '
         'the top so that they match the job posting.'),
    ],
    body='''
<p>A resume has one job: to get a human being to spend ninety seconds on you instead of
thirty. Everything below is in service of that. If a line does not help a stranger decide
that you can do the work, it is taking up space that a better line could use.</p>

<h2 id="order">The order of the page</h2>
<p>There is a conventional order, and deviating from it costs you more than it gains. Top
to bottom:</p>
<ol>
  <li><strong>Name and contact details.</strong> Name, city, email, phone, and a link if the
  link is relevant to the work.</li>
  <li><strong>A short summary.</strong> Two or three lines. Optional, but useful when your
  job title does not obviously match the one you are applying for.</li>
  <li><strong>Work experience,</strong> most recent first.</li>
  <li><strong>Education,</strong> most recent first. Move this above work experience only if
  you graduated in the last year or the qualification is the point of the job.</li>
  <li><strong>Skills.</strong> Tools, languages, certifications. Short and concrete.</li>
  <li><strong>Anything else</strong> that earns its place: publications, open source, licences,
  volunteering with real responsibility.</li>
</ol>
<p>Sections a reader expects to find in a certain place get read. Sections in unusual places
get skipped, and an unusual layout does not read as creative — it reads as work.</p>

<h2 id="contact">The contact block</h2>
<p>Four things: your name, the city and country you can work from, an email address you
check, and a phone number. That is the whole list.</p>
<p>Use an email address that is your name. An address you made when you were fourteen is a
distraction, and the recruiter has to type it into a system where other people will see it.
Drop your full postal address: nobody posts letters, and a street address in a database is a
liability for both of you. Add a link only when it shows work — a portfolio, a code host, a
professional profile you have actually kept current. A dead link is worse than none.</p>

<div class="callout">
<strong>Right to work</strong>
<p>If you need sponsorship, or you already have the right to work somewhere that your address
does not imply, say so in one short line near your contact details. Recruiters filter on it,
and leaving them to guess means being filtered out.</p>
</div>

<h2 id="experience">Work experience, the part that matters</h2>
<p>Each role gets a heading and between two and six bullet points. The heading carries your
job title, the employer, the location, and the months and years. Spell the months out or use
the same numeric format throughout; a reader should never have to work out whether 04/06 is
April 2006 or June 2004.</p>
<p>Then the bullet points. A bullet point is not a description of your duties. Your duties are
implied by your job title. A bullet point is evidence that you did the job well, which means
it needs a result in it.</p>

<div class="compare">
  <div class="bad">
    <h4>Duty</h4>
    <p>Responsible for the monthly newsletter and social media channels.</p>
    <p>Handled customer complaints and escalations.</p>
  </div>
  <div class="good">
    <h4>Evidence</h4>
    <p>Rewrote the monthly newsletter around a single story instead of six; open rate rose
    from 18% to 31% over four issues.</p>
    <p>Took the twenty most common complaints, wrote standard answers for them, and cut
    average first-response time from two days to four hours.</p>
  </div>
</div>

<p>The pattern underneath the good column is: <em>what you did, how you did it, what changed.</em>
Numbers make the change legible, but a number is not compulsory. "Which the finance team now
uses instead of their old spreadsheet" is a result. "Which meant we stopped missing the
Friday deadline" is a result.</p>
<p>Put the strongest two bullet points of your most recent role first. That is the piece of
the page a reader is most likely to actually read.</p>
<p>There is more on this than fits here — see <a href="resume-bullet-points.html">writing work
experience bullet points</a> for the full treatment, including what to do when your work has
no measurable output.</p>

<h2 id="gaps">Gaps, short jobs and the things you would rather hide</h2>
<p>Use years only — 2021&nbsp;–&nbsp;2023 rather than March 2021&nbsp;–&nbsp;January 2023 — and
a four-month gap stops existing. That is not dishonest; it is a level of precision the reader
does not need.</p>
<p>For a gap longer than a year, give it a line of its own with a neutral label: <em>Career
break — caring responsibilities</em>, <em>Parental leave</em>, <em>Full-time study</em>. An
explained gap is a fact. An unexplained gap is a question, and questions get answered by the
reader's imagination.</p>
<p>Leave off a job that lasted six weeks and taught you nothing. You are not filing a tax
return; you are writing an argument, and an argument is allowed to be selective as long as
nothing in it is false.</p>

<h2 id="education">Education</h2>
<p>Qualification, institution, and the year you finished. If you left university more than
five years ago, that is the entire section — no modules, no grades, no societies.</p>
<p>If you are still studying or finished this year, this section moves above work experience
and may carry a little more: the subject of your thesis if it is relevant, a grade if it is
good, a scholarship if it was competitive. Everything else stays off.</p>

<h2 id="skills">Skills</h2>
<p>Concrete nouns only. Programming languages, machines, software, spoken languages,
certifications, licences. No adjectives: everyone claims to be a team player and nobody is
believed, because the claim costs nothing to make.</p>
<p>Delete every rating bar. A five-dot scale next to "Excel" tells a reader nothing they can
act on — your four dots and their four dots are not the same four dots — and sidebar graphics
of that kind are frequently unreadable to the software that parses your file. Say
"Excel including pivot tables and Power Query" instead, and now the sentence contains an
actual claim. The <a href="resume-skills-section.html">skills section guide</a> goes further.</p>

<h2 id="summary">The summary at the top</h2>
<p>Three lines, written last, aimed at this job. It should answer: what are you, how much
experience, and what are you looking for.</p>
<p class="pull">"Warehouse team leader, six years, currently running a shift of fourteen at a
regional distribution centre. Looking to move into inventory planning, where I have covered
for the planner for the last two quarters."</p>
<p>That is worth the space. "Dynamic, results-driven professional with a passion for
excellence" is not, and a recruiter reading a hundred files will have seen it forty times
before lunch. If you cannot write a useful summary, leave it out and let your most recent job
speak first. See <a href="resume-summary.html">the summary at the top</a> for more.</p>

<h2 id="length">Length and layout</h2>
<p>One page if you have under about ten years of experience, two pages after that, and never
three unless you are an academic, in which case the rules here do not apply to you anyway.
The <a href="resume-length.html">length guide</a> covers the edge cases.</p>
<p>Keep the body text at 10 or 11 point, keep the margins at 15mm or wider, and leave white
space alone — it is doing work. A page crammed to the edges signals that you could not decide
what mattered, which is itself information about you.</p>
<p>One typeface. Two at most, and then only one for headings and one for body. Colour is fine
in small amounts: a rule, a heading, a sidebar tint. Colour as decoration is not.</p>

<h2 id="tailor">Tailoring without rewriting</h2>
<p>Read the job posting twice. The first three or four requirements listed are what the hiring
manager actually cares about; the rest is the department's wish list. Then make sure those
three or four things appear on your first page, in the posting's own words.</p>
<p>If the posting says "stakeholder management" and your resume says "worked with other
teams", change your line. Not because software is scanning for the phrase — that story is
mostly overstated — but because the human reader has the posting in their other hand and is
matching it line by line. Make the match easy to see.</p>

<h2 id="checks">The last pass</h2>
<ul class="checklist">
  <li>Read it aloud. Every sentence you stumble over is one a stranger will stumble over too.</li>
  <li>Check the dates add up and no employer name is misspelt, especially the one you are applying to.</li>
  <li>Check your phone number by calling it.</li>
  <li>Save as PDF unless you were asked for something else, and name the file
  <em>Firstname-Lastname-Resume.pdf</em>, not <em>resume-final-v4.pdf</em>.</li>
  <li>Open the PDF on a phone. Half of first reads happen there.</li>
  <li>Hand it to someone who does not know your job and ask them what you do. If they cannot
  tell you, the page is not finished.</li>
</ul>
''',
)

# ==================================================================== 2
guide(
    slug='ats-friendly-resume',
    short='Getting past the ATS',
    h1='How applicant tracking systems actually read your resume',
    title='ATS-friendly resumes: what really happens to your file',
    description='What an applicant tracking system does with your resume, what genuinely '
                'breaks parsing, and which of the common warnings are myths.',
    dek='Applicant tracking software is blamed for a lot of rejections it had nothing to do '
        'with. Here is what it actually does to your file, what genuinely breaks, and which '
        'of the usual warnings you can ignore.',
    tag='Getting read',
    minutes=9,
    related=['resume-file-format', 'how-to-write-a-resume', 'resume-skills-section'],
    faq=[
        ('Do applicant tracking systems reject resumes automatically?',
         'Almost never on their own. The usual system ranks and filters, and a human decides '
         'what to do with the ranking. Automatic rejection normally happens on knockout '
         'questions in the application form — right to work, licences, salary — not on the '
         'resume file itself.'),
        ('Is a PDF safe to upload?',
         'Yes, as long as it contains real text rather than a scan or an image. Every major '
         'system has parsed PDFs for years. The exception is a posting that explicitly asks '
         'for .doc or .docx, in which case send what was asked for.'),
        ('Do two-column resumes break parsers?',
         'Modern parsers usually handle them, but "usually" is doing real work in that '
         'sentence. If the application goes through a portal you do not recognise, a single '
         'column removes the risk for free.'),
    ],
    body='''
<p>An applicant tracking system is a database with a careers page bolted to the front. When
you upload a file, three things happen: the text is extracted, the extracted text is sorted
into fields, and the result is stored as a candidate record. Everything people call "the ATS
rejecting you" is a consequence of one of those three steps going badly — or of a human
reading the record afterwards and not being impressed.</p>

<h2 id="extract">Step one: getting the text out</h2>
<p>The parser needs actual text. A PDF exported by a word processor or by a browser's print
function contains text and parses fine. A PDF that is a photograph of a page, or a design
exported as one flat image, contains no text at all — and that is the one genuine catastrophe
in this whole subject, because the resulting record is blank.</p>
<div class="callout warn">
<strong>The one test that matters</strong>
<p>Open your PDF, select all, copy, and paste into a plain text editor. If your name, your
job titles and your bullet points come out as text you can read, the parser will manage.
If you get nothing, or gibberish, fix that before worrying about anything else on this page.</p>
</div>

<h2 id="fields">Step two: sorting it into fields</h2>
<p>The parser looks for landmarks — a heading it recognises, a date range, something shaped
like an email address — and uses them to decide which text is your employment history, which
is education, and which is contact details. This is where a clever layout costs you.</p>
<p>What confuses it, in rough order of how often it actually causes damage:</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>Thing</th><th>What happens</th><th>Worth changing?</th></tr>
  <tr><td>Contact details in the header or footer of the page</td>
      <td>Some parsers never read the header region; your phone number disappears</td>
      <td>Yes, always. Put them in the body.</td></tr>
  <tr><td>Text inside images or icons</td>
      <td>Invisible to the parser. An envelope icon with no text beside it is nothing</td>
      <td>Yes. Keep a text label next to every icon.</td></tr>
  <tr><td>Invented section headings ("My Journey", "What Drives Me")</td>
      <td>The parser cannot classify the block, so the content lands in a bucket nobody reads</td>
      <td>Yes. Use <em>Experience</em>, <em>Education</em>, <em>Skills</em>.</td></tr>
  <tr><td>Tables used for layout</td>
      <td>Some parsers read a table row across the whole page, merging two columns into one line</td>
      <td>Often. Test first, per the copy-paste check above.</td></tr>
  <tr><td>Two-column layouts</td>
      <td>Usually fine now; occasionally interleaves the columns</td>
      <td>Only for portals you do not recognise.</td></tr>
  <tr><td>Skill rating bars and charts</td>
      <td>Parsed as nothing at all — the rating carries no text</td>
      <td>Yes, but mainly because they tell human readers nothing either.</td></tr>
</table>
</div>

<h2 id="rank">Step three: the ranking, and the myths around it</h2>
<p>Recruiters search the database the way anyone searches anything: they type what the job
needs and look at who comes back. Some systems also score candidates against the posting.
Two persistent myths deserve killing here.</p>
<p><strong>White text stuffed with keywords.</strong> Every serious system strips formatting
before indexing, so the hidden text is read exactly like normal text — and then a human opens
the file, sees a paragraph of invisible nonsense, and you are done. People have been
blacklisted from companies for this.</p>
<p><strong>"92% of resumes are rejected by robots."</strong> This number is a quote from a
conference talk about one company's screening questions and has been repeated for a decade
without a source. The systems rank; people decide.</p>
<p>What genuinely helps is dull: use the words the posting uses. If it says "accounts
payable", write accounts payable, not "AP" and not "supplier invoicing". Write both the
spelled-out term and the acronym once — "search engine optimisation (SEO)" — because you
cannot know which one was typed into the search box.</p>

<h2 id="build">Building one that parses</h2>
<ul class="checklist">
  <li>Standard headings: Experience, Education, Skills. Nothing inventive.</li>
  <li>Contact details in the body of the first page, as text.</li>
  <li>One consistent date format, on the same line as the job title or directly under it.</li>
  <li>A single column if the portal is unfamiliar; among our layouts, Plainfield, Linden and
  Hairline are the safe ones.</li>
  <li>Bullet points as real list items, not drawn shapes.</li>
  <li>PDF, unless the posting names a different format.</li>
  <li>The copy-paste test, every time you export.</li>
</ul>
<p>None of this requires an ugly document. It rules out decoration that was not helping a
human reader either.</p>

<h2 id="after">And then a person reads it</h2>
<p>Clearing the parser gets your record into the database with the fields in the right places.
It does not get you an interview. The reason most applications end is still that a person read
the first third of the page and did not see the job they are hiring for. Spend your remaining
effort there: on the <a href="resume-summary.html">summary</a> and the
<a href="resume-bullet-points.html">first three bullet points</a>.</p>
''',
)

# ==================================================================== 3
guide(
    slug='resume-bullet-points',
    short='Writing bullet points',
    h1='Writing work experience bullet points',
    title='Resume bullet points: how to write them, with before and after',
    description='The formula for a bullet point that earns its line, what to do when your '
                'work has no numbers, and twenty verbs that are not "responsible for".',
    dek='The bullet points under your current job are the only part of a resume that most '
        'readers read properly. They are worth more of your time than the rest of the page '
        'put together.',
    tag='Writing it',
    minutes=8,
    related=['how-to-write-a-resume', 'resume-summary', 'resume-mistakes'],
    faq=[
        ('How many bullet points per job?',
         'Three to six for your current or most recent role, two to four for the one before, '
         'one or two for anything older than about eight years. Older roles are context, not '
         'evidence.'),
        ('What if my work has no measurable results?',
         'Use scale, frequency or consequence instead of a percentage. "For a team of forty", '
         '"every fortnight", "which ended the Friday deadline problem" all locate the work '
         'without inventing a metric.'),
        ('Should bullet points be full sentences?',
         'No. Start with a verb, drop the "I", and leave the full stop off or on — just be '
         'consistent. "Rebuilt the onboarding pack for new hires" is the shape you want.'),
    ],
    body='''
<p>A reader gives your resume somewhere between seven and ninety seconds. Nearly all of that
attention lands on the same place: the job title at the top of your experience section, and
the bullet points underneath it. Get those right and the rest of the page is a formality.</p>

<h2 id="formula">What a bullet point is for</h2>
<p>Your job title already tells the reader what you were responsible for. A bullet point that
repeats your responsibilities has spent a line saying nothing. What the reader does not know
is whether you were any good, and the only way to show that on paper is a result.</p>
<p class="pull">Verb — what you did — what changed as a result.</p>
<p>That is the whole formula. The verb goes first because it is the most useful word in the
sentence and the eye lands there. "What changed" is the part most people leave off, and it is
the part that does the convincing.</p>

<div class="compare">
  <div class="bad">
    <h4>Before</h4>
    <p>Responsible for managing the company's social media accounts.</p>
    <p>Assisted with the annual audit.</p>
    <p>Worked on improving the onboarding process for new employees.</p>
  </div>
  <div class="good">
    <h4>After</h4>
    <p>Ran four social accounts for a 60-person firm; grew combined following from 3,000 to
    11,000 in eighteen months by posting customer stories instead of product news.</p>
    <p>Prepared the schedules for the annual audit and answered auditor queries directly,
    which took two weeks off the previous year's sign-off.</p>
    <p>Rebuilt the onboarding pack and first-week plan; new starters now reach their first
    independent task in three days instead of two weeks.</p>
  </div>
</div>

<h2 id="numbers">When there are no numbers</h2>
<p>Plenty of good work produces nothing you can put a percentage on. Nurses, teachers,
administrators, researchers, carers — the value is real and the spreadsheet does not exist.
Reach for one of these instead:</p>
<ul>
  <li><strong>Scale.</strong> How many people, how much money, how many sites, how large a
  caseload. "A caseload of thirty-five" tells a reader more than any adjective.</li>
  <li><strong>Frequency.</strong> Daily, every fortnight, four times a year. It separates the
  thing you did once from the thing you owned.</li>
  <li><strong>Consequence.</strong> What stopped going wrong. "Which ended the recurring
  duplicate-invoice problem" is a result with no number in it.</li>
  <li><strong>Audience.</strong> Who received the work. A report read by the board is not the
  same report read by your line manager.</li>
  <li><strong>Difficulty.</strong> What made it hard. "During the site move, with the old
  system still live" is worth a clause.</li>
</ul>
<div class="callout">
<strong>Estimating honestly</strong>
<p>If you know a number roughly, use it roughly: "around forty tickets a week", "about a
third of the department". A reader can tell the difference between an estimate and a fiction,
and an estimate you can explain in an interview is safe. One you cannot is not.</p>
</div>

<h2 id="verbs">Verbs worth using</h2>
<p>Not because a list of strong verbs is magic, but because the verb you choose forces you to
be specific about what you actually did.</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>You built something</th><td>Built, designed, wrote, launched, introduced, set up, drafted</td></tr>
  <tr><th>You improved something</th><td>Rewrote, simplified, cut, shortened, automated, consolidated, repaired</td></tr>
  <tr><th>You ran something</th><td>Ran, led, coordinated, scheduled, chaired, oversaw, owned</td></tr>
  <tr><th>You worked out something</th><td>Investigated, analysed, tested, traced, audited, reconciled</td></tr>
  <tr><th>You persuaded someone</th><td>Negotiated, presented, trained, advised, briefed, won</td></tr>
</table>
</div>
<p>Words to leave out: <em>responsible for</em>, <em>assisted with</em>, <em>helped to</em>,
<em>worked on</em>, <em>tasked with</em>, <em>involved in</em>. Each of them hides how much of
the work was yours, and a reader assumes the least flattering reading.</p>

<h2 id="order">Order and length</h2>
<p>Strongest first. Not chronological, not "the one I do most often" — the one that would most
impress the person hiring. Readers stop early, so nothing good should be at the bottom.</p>
<p>Two lines maximum per bullet point, one if you can. A bullet point running to four lines is
a paragraph wearing a disguise, and paragraphs in this position do not get read. If it takes
four lines, it is probably two bullet points.</p>

<h2 id="honesty">Where the line is</h2>
<p>Take credit for work you led, work you did, and your share of work a team did — "as part of
the three-person team that…" is both honest and impressive. Do not take credit for a result
you were merely nearby for. Interviews are where this unravels, and it unravels in the first
follow-up question: <em>how did you measure that?</em></p>
<p>Every bullet point on your page should be one you would be happy to spend five minutes
talking about. If you would not, cut it.</p>
''',
)

# ==================================================================== 4
guide(
    slug='resume-summary',
    short='The summary at the top',
    h1='The summary at the top, and when to leave it out',
    title='Resume summary: what to write in three lines (with examples)',
    description='When a resume summary helps, when it wastes the best space on the page, '
                'and how to write one in three lines. Examples for six situations.',
    dek='The three lines under your name are the most expensive space on the page. They are '
        'worth using when your next job is not the obvious continuation of your last one — '
        'and worth deleting when it is.',
    tag='Writing it',
    minutes=6,
    related=['how-to-write-a-resume', 'career-change-resume', 'resume-bullet-points'],
    faq=[
        ('Objective or summary?',
         'Summary. An objective states what you want; a summary states what you are and what '
         'you are aiming at. The old objective format spends the reader\'s attention on your '
         'wishes before establishing why they should care.'),
        ('Should I write it in the first person?',
         'Write it without pronouns at all. "Warehouse team leader, six years" reads as a '
         'label; "I am a warehouse team leader" reads as a cover letter that wandered in.'),
        ('How long should it be?',
         'Two or three lines. Four is a paragraph, and paragraphs at the top of a resume are '
         'skipped by most readers.'),
    ],
    body='''
<p>A summary is a bridge. It exists to connect what you have obviously been doing with the
job you are now applying for, in the two seconds before the reader's eye reaches your most
recent job title.</p>
<p>Which means: if your most recent job title <em>is</em> the job you are applying for, the
bridge spans nothing. Delete it and let your experience start higher up the page.</p>

<h2 id="when">When it earns its space</h2>
<ul>
  <li>You are changing field, and your job titles do not suggest the new one.</li>
  <li>Your title is company-specific and means nothing outside — "Analyst II", "Consultant,
  Grade 3".</li>
  <li>You are applying up a level, and the case for that is not obvious from the page.</li>
  <li>You have been out of work for a while and want to frame that before the dates do it
  for you.</li>
  <li>You are senior enough that the shape of a fifteen-year career needs one sentence of
  orientation.</li>
</ul>
<p>Otherwise, skip it. Nobody has ever been rejected for not having a summary.</p>

<h2 id="write">The three lines</h2>
<p>Line one: what you are and how long. Line two: the most convincing concrete thing you have
done. Line three: what you are looking for, in the words of the posting.</p>

<div class="compare">
  <div class="bad">
    <h4>Says nothing</h4>
    <p>Dynamic and results-oriented professional with a proven track record of success in
    fast-paced environments. Excellent communication skills and a passion for delivering
    value to stakeholders.</p>
  </div>
  <div class="good">
    <h4>Says something</h4>
    <p>Warehouse team leader, six years, currently running a fourteen-person shift at a
    regional distribution centre. Cut mis-picks by a third by rebuilding how the night shift
    hands over. Looking to move into inventory planning, which I have covered for two quarters.</p>
  </div>
</div>

<h2 id="examples">Five more, for five situations</h2>

<h3>Changing field</h3>
<p>Secondary school teacher moving into instructional design. Eight years teaching sciences,
the last three writing the department's schemes of work and training four new staff on them.
Looking for a role building course material for adult learners.</p>

<h3>First job after studying</h3>
<p>Civil engineering graduate (2:1, Leeds), with a final-year project on bridge fatigue
monitoring and a twelve-month placement at a contractor on site inspections. Looking for a
graduate structural role in the north of England.</p>

<h3>Returning after a break</h3>
<p>Management accountant, nine years in manufacturing, returning after two years of full-time
caring. Last role: month-end close and forecasting for three sites, £40m combined turnover.
Fully up to date on the current close software, having recertified this spring.</p>

<h3>Company-specific job title</h3>
<p>Operations analyst — in practice, the person who owns the reporting the sales directors
use. Built the weekly pipeline report used by twelve regional teams and cut its preparation
from two days to two hours. Looking for a revenue operations role with the same remit.</p>

<h3>Senior, many roles</h3>
<p>Head of engineering, fifteen years across payments and logistics, teams of eight to
forty-five. Twice hired and grown a team through a company's first period of real scale.
Looking for a technical leadership role at a company between fifty and two hundred people.</p>

<div class="callout">
<strong>Write it last</strong>
<p>You cannot summarise a page that does not exist yet. Write the experience section first,
then read it back and ask what a stranger would miss. The summary is the answer to that
question, and it takes about ten minutes once the rest is done.</p>
</div>

<h2 id="tailor">Change these three lines, not the whole document</h2>
<p>This is the part of the resume to rewrite per application. Swap the third line for the
posting's own description of the role, move the most relevant achievement into line two, and
you have tailored the document in five minutes without touching anything you might break.</p>
''',
)

# ==================================================================== 5
guide(
    slug='resume-skills-section',
    short='The skills section',
    h1='The skills section, written so it means something',
    title='Resume skills section: what to list and what to delete',
    description='Which skills belong on a resume, how to phrase them so they carry '
                'information, and why rating bars and soft-skill adjectives should go.',
    dek='Most skills sections are a word cloud. A good one is a short, checkable list of '
        'things you can do, phrased so that a reader knows what they are getting.',
    tag='Writing it',
    minutes=7,
    related=['ats-friendly-resume', 'how-to-write-a-resume', 'resume-mistakes'],
    faq=[
        ('Should I include soft skills?',
         'Not as a list. "Communication, teamwork, leadership" is unverifiable and universal. '
         'Show those in a bullet point instead — the sentence about training four new staff '
         'is evidence of all three.'),
        ('How many skills should I list?',
         'Eight to fifteen concrete items, grouped. Beyond that the list stops being read and '
         'starts being scrolled past.'),
        ('Where should the skills section go?',
         'Below experience for anyone with a few years behind them, above it for a first '
         'resume or a career change, where the skills are the argument.'),
    ],
    body='''
<p>The skills section is the easiest part of a resume to write badly, because anything can be
typed into it and nothing in it has to be true in any checkable way. Which is exactly why
readers discount it — unless it contains the kind of detail that only someone who has done
the work would write.</p>

<h2 id="belongs">What belongs in it</h2>
<p>Nouns a person could test you on:</p>
<ul>
  <li><strong>Software and tools</strong> — named, and where the name is ambiguous, qualified.</li>
  <li><strong>Technical methods</strong> — the specific ones you have used, not the category.</li>
  <li><strong>Languages</strong> — with an honest level (see below).</li>
  <li><strong>Certifications and licences</strong> — with the year, and the issuer where it matters.</li>
  <li><strong>Equipment</strong> — machines, instruments, vehicles, anything with a model
  number that a hiring manager would recognise.</li>
</ul>
<p>What does not belong: adjectives about yourself, anything you used once in a course three
years ago, and any skill so basic in your field that listing it raises a question. An
accountant listing "Microsoft Excel" with nothing after it invites the thought that Excel is
worth mentioning.</p>

<h2 id="phrase">Phrasing that carries information</h2>
<div class="compare">
  <div class="bad">
    <h4>Word cloud</h4>
    <p>Excel · SQL · Communication · Project management · Teamwork · Problem solving ·
    Photoshop · Time management · Leadership · Microsoft Office</p>
  </div>
  <div class="good">
    <h4>List</h4>
    <p><strong>Data:</strong> SQL (Postgres, daily), Excel to Power Query and pivot models,
    Power BI dashboards<br>
    <strong>Systems:</strong> SAP FI/CO, Netsuite, Xero<br>
    <strong>Languages:</strong> German (native), English (C1, working language for four years)<br>
    <strong>Certified:</strong> PRINCE2 Practitioner (2024), forklift counterbalance (2023)</p>
  </div>
</div>
<p>The right-hand version is barely longer and every item in it is a claim someone could
check. That is the difference between a section a reader skims and one they use.</p>

<h2 id="bars">Delete the rating bars</h2>
<p>Four dots out of five next to "Photoshop" is information-free. Your four dots and the
reader's four dots are not calibrated against anything, self-assessment is famously unreliable
in both directions, and a graphic bar contains no text — so the parser reading your file gets
"Photoshop" with no rating at all, or nothing whatsoever. Write the level in words, and only
where a level is meaningful.</p>
<p>Languages are the exception, because there is an actual standard. Use the CEFR levels
(A1&nbsp;–&nbsp;C2) in Europe, or plain words elsewhere: native, fluent, working knowledge,
basic. "Conversational" means you cannot work in it; say so rather than letting someone find
out on the call.</p>

<h2 id="group">Group them</h2>
<p>Three or four labelled groups beat one long line, because the labels let a reader find what
they came for. Use the groups that fit your field: <em>Languages / Software / Certifications</em>,
or <em>Clinical / Administrative / Systems</em>, or <em>Machines / Materials / Safety</em>.</p>

<div class="callout">
<strong>Match the posting's vocabulary</strong>
<p>If the job says "MS Dynamics 365" and you wrote "Dynamics", write it their way once. Do the
same with acronyms in both directions — "search engine optimisation (SEO)" — because you
cannot know which form the recruiter typed into the search box. This is the whole of what
keyword matching requires; anything beyond it is <a href="ats-friendly-resume.html">folklore</a>.</p>
</div>

<h2 id="where">Where to put it</h2>
<p>If you have worked for a few years, skills go below your experience: your jobs are the
evidence, and the list is a reference. If this is your <a href="first-resume-no-experience.html">first
resume</a> or you are <a href="career-change-resume.html">changing field</a>, move it up, because
the list <em>is</em> your argument and the reader needs it before the job history explains why
you are not an obvious fit.</p>

<h2 id="prove">Prove one of them</h2>
<p>The strongest move available here is small: make sure at least one skill in the list also
appears inside a bullet point, doing something. "SQL" in the list and "rebuilt the weekly
pipeline report in SQL, cutting preparation from two days to two hours" in the experience
section turns an unverifiable claim into a story. Do that for the two or three skills the job
actually turns on.</p>
''',
)

# ==================================================================== 6
guide(
    slug='resume-length',
    short='One page or two',
    h1='One page or two',
    title='Resume length: when one page is right and when two is better',
    description='How long a resume should be, by career stage and country, and what to cut '
                'first when you need to lose half a page.',
    dek='The one-page rule is American, roughly twenty years old, and applied far more widely '
        'than it deserves. Here is the version that survives contact with reality.',
    tag='Getting read',
    minutes=5,
    related=['how-to-write-a-resume', 'lebenslauf-german-resume', 'resume-mistakes'],
    faq=[
        ('Is a two-page resume acceptable?',
         'Yes, once you have roughly ten years of relevant experience. Below that, two pages '
         'usually means the first page has not been edited.'),
        ('What if my resume is one and a half pages?',
         'Cut it to one or extend it to two. A half-empty second page reads as an accident; '
         'it is the one length to avoid.'),
        ('Does a longer resume mean more keywords and better ranking?',
         'No. Padding dilutes the page for the human reader, and search ranking is not driven '
         'by repetition in any system worth worrying about.'),
    ],
    body='''
<p>Length is a proxy for editing. A reader does not object to a second page; they object to
reading three hundred words to learn something a hundred would have covered. The question is
never "how long may it be" but "is everything on it pulling its weight".</p>

<h2 id="rule">The working rule</h2>
<div class="scroll-x">
<table class="plain">
  <tr><th>Situation</th><th>Length</th></tr>
  <tr><td>Student, graduate, first job</td><td>One page, and it will not be full. That is fine.</td></tr>
  <tr><td>Up to about ten years of experience</td><td>One page</td></tr>
  <tr><td>More than ten years, or several employers worth describing</td><td>Two pages</td></tr>
  <tr><td>Senior leadership, twenty years plus</td><td>Two pages. Still two.</td></tr>
  <tr><td>Academic CV, medicine, research</td><td>As long as the publication list requires — different document, different rules</td></tr>
  <tr><td>Germany, Austria, Switzerland</td><td>One to two pages, plus the certificate attachments the application expects</td></tr>
</table>
</div>
<p>The one length to avoid is a page and a bit. It looks like a document that ran out of
attention rather than one that was finished.</p>

<h2 id="cut">What to cut first</h2>
<p>In this order, and you will usually find your half page before reaching the end:</p>
<ol>
  <li><strong>Jobs older than fifteen years.</strong> Collapse them into one line:
  <em>Earlier: retail and hospitality roles, 2004&nbsp;–&nbsp;2010.</em></li>
  <li><strong>Duties dressed as achievements.</strong> Any bullet point without a result.</li>
  <li><strong>The third, fourth and fifth bullet points of old roles.</strong> Two each is plenty
  beyond the last decade.</li>
  <li><strong>Education detail below the highest qualification.</strong> Once you have a degree,
  school results are noise.</li>
  <li><strong>The interests line,</strong> unless a specific interest is genuinely relevant to
  this employer.</li>
  <li><strong>"References available on request."</strong> Everyone knows. It is four words of
  nothing.</li>
  <li><strong>The address block.</strong> City and country are enough.</li>
</ol>

<div class="callout warn">
<strong>What not to do to save space</strong>
<p>Do not drop the body text below 10 point, do not squeeze margins under 12mm, and do not
remove the white space between sections. A cramped page is read less carefully than a page
with a bit of air, which defeats the purpose of fitting more onto it.</p>
</div>

<h2 id="two">Making two pages work</h2>
<p>If you go to two, the second page has to be worth turning to. Put your name and a page
number on it — pages get separated when printed. Do not split a single job across the page
break. Keep the strongest material in the top half of page one regardless; nobody decides to
interview you on the strength of page two.</p>

<h2 id="fill">If you cannot fill one page</h2>
<p>Do not stretch. Enlarged type and inflated spacing are visible from across a room. A short,
clean, well-spaced page is entirely normal for a first resume — see
<a href="first-resume-no-experience.html">your first resume</a> for what to put on it besides
jobs. Among our layouts, the ones with generous headers — Vesper, Slate, Linden — carry a
shorter document better than the dense two-column ones.</p>
''',
)

# ==================================================================== 7
guide(
    slug='resume-file-format',
    short='PDF, Word or text',
    h1='PDF, Word or plain text: which file to send',
    title='Resume file format: PDF or Word, and how to name the file',
    description='Which file format to send a resume in, when Word is the right answer, '
                'how to name the file, and how to check the PDF before you send it.',
    dek='PDF, almost always. But "almost" covers a few situations that matter, and there are '
        'three checks worth running on the file before it leaves your machine.',
    tag='Sending it',
    minutes=6,
    related=['ats-friendly-resume', 'how-to-write-a-resume', 'resume-mistakes'],
    faq=[
        ('Is PDF or Word better for a resume?',
         'PDF, unless the posting or the recruiter asks for Word. PDF keeps your layout '
         'identical on every machine; Word documents reflow and can arrive looking broken.'),
        ('Why would a recruiter want a Word file?',
         'Agency recruiters often strip your contact details and add their own branding before '
         'sending you to a client. That requires an editable file. It is a legitimate request '
         'from an agency and an unusual one from an employer.'),
        ('How should I name the resume file?',
         'Firstname-Lastname-Resume.pdf, optionally with the company name. It is what appears '
         'in a folder of two hundred files, and "resume-final-v3.pdf" makes yours the hard one '
         'to find.'),
    ],
    body='''
<p>Send a PDF. It looks the same on every machine, it cannot be edited by accident, it prints
predictably, and every applicant tracking system has parsed PDFs for years. The rest of this
page is the exceptions and the checks.</p>

<h2 id="word">When to send Word instead</h2>
<ul>
  <li><strong>The posting asks for it.</strong> Then send it. Ignoring an explicit instruction
  in the first interaction is its own kind of answer.</li>
  <li><strong>An agency recruiter asks for it.</strong> They will re-brand the document before
  passing it to their client, which needs an editable file.</li>
  <li><strong>An upload form rejects PDFs.</strong> Rare, and usually an old internal system.</li>
</ul>
<p>When you do send Word, open the file on a second machine first. Fonts you have installed and
the recipient does not will be substituted, and substitution moves everything. Stick to Arial,
Calibri, Times New Roman or Georgia in a Word version and the damage is limited.</p>

<div class="callout">
<strong>Both, if a person is reading</strong>
<p>When you are emailing a human being directly, attaching the PDF is right. When you are
uploading into a portal that accepts one file, the PDF is still right. There is no situation
that calls for attaching both, and doing so makes the reader choose.</p>
</div>

<h2 id="never">Formats not to send</h2>
<p><strong>Pages, ODT or an obscure design format:</strong> the recipient may not be able to
open it at all. <strong>A scan or a photograph of a printed page:</strong> it contains no text,
so the parser records an empty candidate. <strong>A link instead of a file:</strong> now the
reader has to click, wait, and possibly log in. <strong>A ZIP:</strong> some mail systems strip
them outright.</p>

<h2 id="checks">Three checks before it goes</h2>
<ul class="checklist">
  <li><strong>The copy-paste test.</strong> Open the PDF, select all, copy, paste into a plain
  text editor. If your name and bullet points come out as readable text, any parser will cope.
  If nothing comes out, the file is an image and needs re-exporting.</li>
  <li><strong>The phone test.</strong> Mail it to yourself and open it on a phone. A large share
  of first reads happen on a phone screen, and a layout with 9 point text in a narrow sidebar
  falls apart there.</li>
  <li><strong>The metadata test.</strong> Check the document title in your PDF reader's
  properties panel. Exports often inherit a filename like "Untitled-3" or, worse, the name of
  whoever's template you started from.</li>
</ul>

<h2 id="print">Exporting cleanly from a browser</h2>
<p>The editor on this site exports through your browser's print dialogue, which produces a
proper text PDF. Two settings decide whether it comes out right:</p>
<ul>
  <li><strong>Margins: none.</strong> The page already has its own margins; the browser adding
  more shrinks everything and can push a line onto a second page.</li>
  <li><strong>Background graphics: on.</strong> Without it, every tinted sidebar and coloured
  header prints white, which on some layouts removes half the design.</li>
</ul>
<p>Then check the page count in the preview before saving. It is the moment a stray blank
second page is easiest to catch.</p>

<h2 id="naming">The filename</h2>
<p><code>Anna-Weber-Resume.pdf</code>. Add the company if you like —
<code>Anna-Weber-Resume-Siemens.pdf</code> — but check you changed it before sending it to the
next employer. In a folder of two hundred applications, a file named after you is the one a
recruiter can find again after lunch.</p>
''',
)

# ==================================================================== 8
guide(
    slug='first-resume-no-experience',
    short='Your first resume',
    h1='Your first resume, with no work experience',
    title='How to write your first resume with no experience',
    description='What to put on a resume when you have never had a job: coursework, '
                'projects, volunteering and part-time work, arranged so the page holds up.',
    dek='An empty experience section is not an empty page. The material is there — it is just '
        'filed under coursework, part-time work and things you did because you wanted to.',
    tag='Special cases',
    minutes=8,
    related=['resume-summary', 'resume-skills-section', 'resume-length'],
    faq=[
        ('What if I have genuinely never worked?',
         'Then the page is built from education, projects, volunteering and responsibilities. '
         'Course projects with a real output, a society you ran, a sports team you organised '
         '— all of it is evidence of doing something to a standard by a deadline.'),
        ('Should I include my school grades?',
         'Include them while they are your most recent qualification, and drop them once you '
         'have a higher one or two years of work behind you.'),
        ('Is a one-page resume too short for a first job?',
         'No. Employers hiring for entry-level roles expect one page and are not surprised by '
         'white space. Padding is more obvious than shortness.'),
    ],
    body='''
<p>Everyone hiring for an entry-level role knows you have not done the job before. That is what
entry level means. What they are looking for on your page is narrower and much easier to
supply: evidence that you finish things, that you can be relied on, and that you have some
specific reason for wanting this work rather than any work.</p>

<h2 id="order">Put education first</h2>
<p>For your first resume the order changes: contact details, a short summary, education, then
everything else. Your education is your most substantial item and it belongs where the reader
looks first.</p>
<p>Under the qualification, add two or three lines of substance — but only real substance:</p>
<ul>
  <li>A final-year project or thesis, with what it produced.</li>
  <li>Modules that are genuinely relevant to the job. Two or three, not the whole transcript.</li>
  <li>A grade, if it is good. Silence is a perfectly acceptable alternative.</li>
  <li>A scholarship, prize or competitive placement.</li>
</ul>

<h2 id="counts">What counts as experience</h2>
<p>More than you think. Give each of these the same treatment as a job — heading, dates,
bullet points with results:</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>This</th><th>Reads as</th></tr>
  <tr><td>Part-time or holiday work, any field</td><td>Reliability, customer contact, working under supervision, showing up</td></tr>
  <tr><td>Course projects with an output</td><td>Doing technical work to a deadline with other people</td></tr>
  <tr><td>Volunteering</td><td>Responsibility taken without being paid to take it</td></tr>
  <tr><td>Running a society, team or event</td><td>Organising other people, budgets, logistics</td></tr>
  <tr><td>Freelance or self-taught work</td><td>Initiative, and often the exact skills the job needs</td></tr>
  <tr><td>Caring for a family member</td><td>Genuine responsibility; also explains a gap</td></tr>
</table>
</div>
<p>Call the section <em>Experience</em> and let it contain a mix. It does not need to be
called "Relevant experience" — the reader can see what is in it.</p>

<div class="compare">
  <div class="bad">
    <h4>Thin</h4>
    <p>Café assistant, Café Rondo, 2024&nbsp;–&nbsp;2025<br>
    Served customers and handled the till.</p>
  </div>
  <div class="good">
    <h4>Same job, written properly</h4>
    <p>Café assistant, Café Rondo, 2024&nbsp;–&nbsp;2025<br>
    Opened the café alone three mornings a week, including float, stock check and first
    service.<br>
    Trained two new starters on the till and the morning routine.</p>
  </div>
</div>
<p>Nothing was invented between those two boxes. The second one just says what actually
happened.</p>

<h2 id="projects">Projects deserve their own section</h2>
<p>If you build, write, design or research anything, a projects section is often the strongest
thing on a first resume, because it is the only part that shows work rather than attendance.</p>
<p>Per project: what it is in one line, what you specifically did, what it used, and where it
can be seen. A link a reader can open in ten seconds is worth more than three lines of
description — and if there is no link, one clear sentence about the outcome will do.</p>

<div class="callout">
<strong>Two is enough</strong>
<p>Two projects you can talk about for ten minutes beat six you half-finished. The interview
will go straight to whatever is on this list, and "I did not get very far with that one" is a
bad way to spend the first question.</p>
</div>

<h2 id="skills">Skills near the top</h2>
<p>On a first resume, move <a href="resume-skills-section.html">skills</a> above experience.
It is the part of the page most likely to match the posting, and it gives the reader something
concrete before the job history explains that you have not done this before. Keep it honest:
"basic" and "learning" are respectable words, and being caught out in the interview is worse
than any gap in the list.</p>

<h2 id="short">A short page is fine</h2>
<p>One page, not full, properly spaced. Do not enlarge the type, do not add an interests
section listing "socialising with friends", and do not write a paragraph about your passion
for the industry. A clean short page reads as someone who knows what they have; a padded one
reads as someone hoping you will not notice.</p>
<p>The one thing genuinely worth adding when the page is light: a line under your contact
details saying what you are looking for and when you are available. It is the question the
reader has, and answering it costs one line.</p>
''',
)

# ==================================================================== 9
guide(
    slug='career-change-resume',
    short='Changing career',
    h1='A resume for a career change',
    title='Career change resume: how to make the jump legible',
    description='How to write a resume when you are changing field: what to translate, '
                'what to lead with, and why the functional resume format is a trap.',
    dek='The problem with a career change is not that your experience is irrelevant. It is '
        'that the relevance is obvious to you and invisible to the person reading.',
    tag='Special cases',
    minutes=8,
    related=['resume-summary', 'resume-skills-section', 'resume-bullet-points'],
    faq=[
        ('Should I use a functional or skills-based resume?',
         'No. Recruiters read the format as an attempt to hide something, and it removes the '
         'dates they use to orient themselves. Keep the reverse-chronological structure and '
         'do the work in the summary and the bullet points.'),
        ('Do I have to explain why I am changing career?',
         'One line in the summary is enough on the resume. The reasoning belongs in the cover '
         'letter, where there is room for it.'),
        ('Should I leave off jobs from my old field?',
         'No — that creates gaps, which cost more than irrelevance. Shorten them instead: one '
         'line of context and one bullet point that translates.'),
    ],
    body='''
<p>You know why your eight years in hospitality prepare you for operations work. The person
reading has forty files and twenty minutes and will not do that translation for you. A career
change resume is an exercise in doing it for them, on the page, in their vocabulary.</p>

<h2 id="functional">First: do not use a functional resume</h2>
<p>The advice to drop the chronology and group everything under skill headings is common and
wrong. Recruiters recognise the format immediately, and what it signals is <em>this person is
hiding a gap, a demotion or a short tenure</em> — so they go hunting instead of reading.
It also removes the dates, which are how a reader builds a mental picture of your career in
the first ten seconds.</p>
<p>Keep the ordinary reverse-chronological structure. Do the work elsewhere.</p>

<h2 id="translate">Translate, do not delete</h2>
<p>Every job you have had contains work that exists in the new field under a different name.
Find those parts and write them in the new field's words.</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>What it was</th><th>What it is called where you are going</th></tr>
  <tr><td>Ran a restaurant shift</td><td>Operations under time pressure; staff scheduling; stock control</td></tr>
  <tr><td>Taught a class of thirty</td><td>Training delivery; curriculum design; managing a room</td></tr>
  <tr><td>Nursing handover and notes</td><td>Documentation to a regulated standard; handover protocols</td></tr>
  <tr><td>Army logistics</td><td>Supply chain coordination; asset tracking; briefing senior stakeholders</td></tr>
  <tr><td>Retail management</td><td>P&amp;L responsibility; hiring and rota; shrinkage and loss prevention</td></tr>
</table>
</div>
<p>This is not spin, provided the underlying facts hold. "Scheduling" is a true description of
writing the rota. What changes is which true description you chose.</p>

<div class="callout warn">
<strong>Where translation becomes fiction</strong>
<p>Calling shift rotas "workforce planning" is fine. Calling yourself a workforce planner is
not. Describe the work in their language; do not award yourself their job title.</p>
</div>

<h2 id="top">Lead with the bridge</h2>
<p>The top third of the page has to make the case before the job titles undermine it. Three
elements, in this order:</p>
<ol>
  <li><strong>A summary</strong> that names the change explicitly. Not apologetically —
  explicitly. "Restaurant manager moving into operations" tells the reader how to read
  everything that follows.</li>
  <li><strong>A skills block</strong> directly underneath, weighted towards the new field:
  the tools, the certifications, the course you finished last spring.</li>
  <li><strong>Then experience,</strong> as normal, with the translated bullet points.</li>
</ol>
<p>See <a href="resume-summary.html">the summary at the top</a> for the three-line pattern;
the career-change example there is the shape you want.</p>

<h2 id="evidence">Close the gap with something recent</h2>
<p>The strongest thing on a career change resume is usually evidence of the new field that is
<em>dated this year</em>: a certification, a course with an assessed output, freelance work,
a volunteer project, a side project someone actually uses. One concrete item beats any amount
of stated enthusiasm, because it shows the decision is already in motion.</p>
<p>Give it real estate. A short <em>Relevant projects</em> or <em>Recent training</em> section
above your experience is worth more than the fifth bullet point of a job you are leaving.</p>

<h2 id="old">Shrinking the old career without hiding it</h2>
<p>Keep every role, keep every date, but change the weight. Your most recent role in the old
field gets two or three bullet points, all of them translated. Roles before that get one line
each: title, employer, dates, and a single clause of context. Anything more than ten years old
collapses into one line for the lot.</p>
<p>You are not concealing your history. You are spending your page on the part that argues for
the next job.</p>

<h2 id="level">Be realistic about level</h2>
<p>A change of field usually costs a step. Applying for roles one level below where you were is
normal, and pretending otherwise produces applications that go nowhere for reasons nobody will
explain to you. What it does not cost is your seniority as a person: someone who has run a
team of twenty is a different junior analyst than someone two years out of university, and
the page should make that visible even while the title is modest.</p>
''',
)

# ==================================================================== 10
guide(
    slug='resume-mistakes',
    short='Mistakes worth fixing',
    h1='Eleven things that get a resume put down',
    title='Common resume mistakes, and what to do instead',
    description='The mistakes that actually cost interviews, ordered by how much damage they '
                'do — and the small fix for each one.',
    dek='Ordered by how much damage they do, not by how often they appear on lists like this. '
        'Most are five-minute fixes.',
    tag='Getting read',
    minutes=7,
    related=['how-to-write-a-resume', 'resume-bullet-points', 'ats-friendly-resume'],
    faq=[
        ('What is the single most common resume mistake?',
         'Describing duties instead of results. Your job title already implies the duties; '
         'the bullet points have to show whether you did them well.'),
        ('Do typos really cost interviews?',
         'Sometimes, and always more than they should. A misspelt employer name is the '
         'expensive one — it reads as not caring which company you are applying to.'),
        ('Is it worth using a template?',
         'Yes, for structure and spacing. The mistake is picking one for decoration: heavy '
         'graphics cost you parsing reliability and, on paper, attention.'),
    ],
    body='''
<h2 id="one">1. Duties where results should be</h2>
<p>"Responsible for the monthly report" describes a job description, not a person. Every bullet
point should contain something that changed because you were there. This is the single most
common weakness, and fixing it is most of the work of a good resume —
<a href="resume-bullet-points.html">the bullet points guide</a> covers how.</p>

<h2 id="two">2. A generic top third</h2>
<p>"Dynamic, results-driven professional with excellent communication skills" occupies the most
valuable space on the page and says nothing. Either write three specific lines or delete the
section and let your most recent job start higher.</p>

<h2 id="three">3. The same file for every application</h2>
<p>You do not need a new resume each time. You do need the summary, the skill order and the top
two or three bullet points to match what the posting asks for, in the posting's words. Ten
minutes, per application.</p>

<h2 id="four">4. A misspelt employer name</h2>
<p>Of all the typos, this one does the most damage: it implies the application is one of fifty
identical ones. Check the company name, the job title in your cover letter, and the hiring
manager's name if you used it. Then read the whole document aloud — your eye skips what your
mouth will not.</p>

<h2 id="five">5. Contact details in the page header</h2>
<p>Some parsers never read the header and footer regions of a document, which means your phone
number and email vanish. Keep them in the body of the page. Same problem with contact icons
that have no text beside them: an envelope glyph parses as nothing.</p>

<h2 id="six">6. Rating bars and skill charts</h2>
<p>Four dots out of five is not information — your scale and the reader's are not the same
scale — and the graphic contains no text for a parser to read. Write the level in words, or
write what you did with the tool.</p>

<h2 id="seven">7. Pages of everything</h2>
<p>Three pages before you have twenty years of experience, or a full list of every course you
have ever attended, tells the reader you could not decide what mattered. That decision is the
job of the document. <a href="resume-length.html">One page or two</a> has the cutting order.</p>

<h2 id="eight">8. Unexplained gaps</h2>
<p>A gap is a fact. An unexplained gap is a question, and readers answer their own questions
unhelpfully. One neutral line — <em>Career break, caring responsibilities, 2023&nbsp;–&nbsp;2024</em>
— closes it. Switching to years-only dates closes a short one entirely.</p>

<h2 id="nine">9. An email address from another era</h2>
<p>Your name, at any ordinary provider. An address made when you were fourteen has to be typed
into a system by someone who will see it again, and it is the one detail on the page you can
fix in two minutes.</p>

<h2 id="ten">10. Photographs where they do not belong</h2>
<p>In the United States, the United Kingdom, Ireland, Canada and Australia, a photo can get the
file discarded outright — some employers have a policy of not looking at applications with one,
to keep discrimination claims away. In Germany, Austria and Switzerland it is still standard
practice. Know which convention applies before you export; see
<a href="lebenslauf-german-resume.html">the German Lebenslauf</a> for the other side of this.</p>

<h2 id="eleven">11. Interests that fill space</h2>
<p>"Socialising with friends, listening to music, travelling" is the resume equivalent of
clearing your throat. An interest earns its line only when it is specific and says something —
a sport you compete in, a thing you build, a language you are learning, something that
genuinely connects to the work. Otherwise the line is better empty.</p>

<div class="callout">
<strong>The two-minute review</strong>
<p>Read only the first third of your page and ask: does this say what I am, how much experience
I have, and one convincing thing I have done? If not, that is where the next hour goes — not
into the bottom half.</p>
</div>
''',
)

# ==================================================================== 11
guide(
    slug='cover-letter',
    short='The cover letter',
    h1='The cover letter, in five paragraphs',
    title='How to write a cover letter that gets read (with a structure)',
    description='When a cover letter matters, the five-paragraph structure that works, and '
                'the openings to avoid. With a worked example.',
    dek='Most cover letters are a prose version of the resume, which is why most go unread. '
        'The useful version answers one question the resume cannot.',
    tag='Sending it',
    minutes=9,
    related=['resume-summary', 'career-change-resume', 'how-to-write-a-resume'],
    faq=[
        ('Does anyone actually read cover letters?',
         'Hiring managers at small and mid-sized employers often do, especially for roles with '
         'few applicants. Large-volume recruiting frequently does not. Writing one is cheap '
         'insurance; writing a generic one is not.'),
        ('How long should a cover letter be?',
         'Between 200 and 350 words. Half a page. Anything longer is competing with the resume '
         'for the same attention.'),
        ('What if there is no named contact?',
         '"Dear hiring team" is fine. Avoid "To whom it may concern", which reads as a form '
         'letter, and avoid guessing a name you are not sure of.'),
    ],
    body='''
<p>A resume says what you have done. A cover letter answers a question the resume structurally
cannot: <em>why this job, at this company, now?</em> If your letter does not answer that, it is
a worse version of a document the reader already has.</p>

<h2 id="when">When it is worth writing</h2>
<ul>
  <li><strong>Always, when the application asks for one.</strong> Not sending it is an answer.</li>
  <li><strong>When you are <a href="career-change-resume.html">changing field</a></strong> — this
  is where the reasoning fits.</li>
  <li><strong>When you have a gap or an unusual path</strong> that benefits from one sentence of
  context.</li>
  <li><strong>When the employer is small.</strong> The person reading is often the person you
  would work for, and they are reading properly.</li>
  <li><strong>When you have a real connection</strong> — a referral, their product, a piece of
  their work you know.</li>
</ul>
<p>For high-volume applications through a large portal, a generic letter adds nothing. Spend
the time tailoring the top of the resume instead.</p>

<h2 id="structure">The five paragraphs</h2>
<ol>
  <li><strong>What you are applying for and the one-line reason you fit.</strong> No throat
  clearing, no "I am writing to apply for". Lead with the fit.</li>
  <li><strong>The best piece of evidence you have,</strong> told as a short story with an
  outcome — a paragraph, not a bullet point. Pick the one closest to the job's main problem.</li>
  <li><strong>The second piece,</strong> covering a different requirement from the posting.</li>
  <li><strong>Why this employer.</strong> Something specific and checkable: their product,
  their market, a change they have announced, the shape of the team. This is the paragraph
  that cannot be reused, and the one people can tell you skipped.</li>
  <li><strong>A plain close.</strong> Available from a date, happy to talk, thank you. One
  line.</li>
</ol>

<div class="compare">
  <div class="bad">
    <h4>Opening that wastes the paragraph</h4>
    <p>I am writing to apply for the position of Operations Coordinator as advertised on your
    website. I believe my skills and experience make me an excellent candidate for this role
    and I would welcome the opportunity to contribute to your team.</p>
  </div>
  <div class="good">
    <h4>Opening that earns the next one</h4>
    <p>I have spent four years keeping a fourteen-person warehouse shift running to a
    two-hour dispatch window, and your coordinator posting is largely a description of that
    with better systems. Two things from it stood out.</p>
  </div>
</div>

<h2 id="example">A worked middle</h2>
<p class="pull">"The posting mentions reducing mis-picks. When I took over the night shift we
were at around 4%. Most of it turned out to be the handover: the day team left notes on paper
and half of them were never read. I moved the handover to a five-minute standing briefing with
a one-page sheet, and mis-picks were under 1.5% within two months and have stayed there."</p>
<p>That paragraph does the work of six bullet points, because it contains a problem, a
diagnosis and a result. One of those per letter is enough; two is the maximum.</p>

<h2 id="avoid">Things to leave out</h2>
<ul>
  <li>Restating your resume in sentences. They have it.</li>
  <li>"I am passionate about…" — assertion with no evidence attached.</li>
  <li>Explaining what the company does back to the company.</li>
  <li>Apologising for what you lack. Address a real gap in one confident clause or not at all.</li>
  <li>Anything about what the job would do for your development. The letter is about what you
  bring.</li>
</ul>

<div class="callout">
<strong>Format and sending</strong>
<p>Same typeface and header as your resume, so the two look like one application. Send as a
separate PDF unless the portal wants one file. If you are emailing directly, the letter can be
the body of the email — but attach it as well, because the body text will not survive being
forwarded into the applicant system.</p>
</div>
''',
)

# ==================================================================== 12
guide(
    slug='lebenslauf-german-resume',
    short='The German Lebenslauf',
    h1='The German Lebenslauf, for anyone applying in the DACH region',
    title='German Lebenslauf: what is different from an English resume',
    description='Photo, signature, Anschreiben and Zeugnisse: what a German, Austrian or '
                'Swiss application expects, and how it differs from a US or UK resume.',
    dek='A German application is a package, not a file. If you are applying with a resume '
        'written for the US or UK market, three things are missing and one thing is in the '
        'wrong place.',
    tag='Special cases',
    minutes=9,
    related=['how-to-write-a-resume', 'resume-length', 'cover-letter'],
    faq=[
        ('Do I need a photo on a German Lebenslauf?',
         'It is not legally required — the AGG discrimination law means an employer may not '
         'demand one — but it remains the norm and most applications include one. A plain, '
         'professional headshot in the header is the convention.'),
        ('What is a tabellarischer Lebenslauf?',
         'The standard format: a two-column table of dates on the left and positions on the '
         'right, reverse-chronological, one to two pages. It is what "Lebenslauf" means in '
         'practice.'),
        ('Do I still need to sign a Lebenslauf?',
         'Signing with place and date is traditional and still common, particularly in public '
         'sector and traditional companies. Nobody will reject a well-made unsigned CV, but '
         'signing costs nothing.'),
    ],
    body='''
<p>If you are applying in Germany, Austria or Switzerland with a document written for the
American or British market, the mismatch is not about quality. It is about what an application
is expected to contain.</p>

<h2 id="package">The application is a package</h2>
<p>A complete German application — the <em>Bewerbung</em> — normally has three or four parts,
sent as one PDF in this order:</p>
<ol>
  <li><strong>Anschreiben</strong> — the cover letter. Expected by default, not optional the
  way it often is elsewhere. One page.</li>
  <li><strong>Lebenslauf</strong> — the CV itself, one to two pages.</li>
  <li><strong>Zeugnisse</strong> — scanned references and certificates: your
  <em>Arbeitszeugnisse</em> from previous employers, your degree certificate, relevant
  qualifications.</li>
  <li>Sometimes a <strong>Deckblatt</strong>, a cover sheet with your photo, name and the
  position. Optional, less common than it was.</li>
</ol>
<p>Sending only a CV to a German employer looks incomplete in the way that sending a resume
with no contact details would look elsewhere.</p>

<h2 id="differences">What differs from a US or UK resume</h2>
<div class="scroll-x">
<table class="plain">
  <tr><th></th><th>US / UK</th><th>DACH</th></tr>
  <tr><td>Photo</td><td>Leave it off; can get the file discarded</td><td>Still the norm; a plain professional headshot</td></tr>
  <tr><td>Date of birth</td><td>Never</td><td>Common, though optional since the AGG</td></tr>
  <tr><td>Signature</td><td>No</td><td>Place, date and signature at the foot; traditional but common</td></tr>
  <tr><td>References</td><td>"On request", or named referees</td><td>Actual scanned Arbeitszeugnisse attached</td></tr>
  <tr><td>Length</td><td>One page under ten years</td><td>One to two pages, plus attachments</td></tr>
  <tr><td>Tone of the letter</td><td>Persuasive, personal</td><td>Formal, factual, precise</td></tr>
  <tr><td>Gaps</td><td>Best glossed with years-only dates</td><td>Expected to be accounted for, month by month</td></tr>
</table>
</div>

<div class="callout warn">
<strong>Do not use one document for both markets</strong>
<p>The photo and date of birth that are normal in Munich are a liability in London or Chicago,
and the years-only dates that tidy a gap in Chicago look evasive in Munich. Keep two exports.
In our editor, that means two saved files — the same content, one with the photo block and
monthly dates, one without.</p>
</div>

<h2 id="structure">Structure of the Lebenslauf</h2>
<p>The <em>tabellarischer Lebenslauf</em> is a two-column table: dates on the left, everything
else on the right. Reverse-chronological is now standard, though older German convention ran
forwards and you will still see it.</p>
<ul>
  <li><strong>Persönliche Daten</strong> — name, address, phone, email; optionally date and
  place of birth, nationality, marital status. The last three are genuinely optional.</li>
  <li><strong>Berufserfahrung</strong> — month/year ranges, employer, place, job title, then
  two to four lines of what the role actually involved.</li>
  <li><strong>Ausbildung</strong> — degrees, then Abitur or equivalent, with grades.
  Grades are expected here in a way they are not in the UK or US.</li>
  <li><strong>Kenntnisse</strong> — languages with CEFR levels, software, certifications,
  driving licence class where relevant.</li>
  <li><strong>Weiterbildung</strong> — courses and training, with dates.</li>
  <li><strong>Ehrenamt / Interessen</strong> — optional, and only where specific.</li>
</ul>
<p>Month and year, not just year: an unexplained two-month gap is more likely to be asked about
here than smoothed over, and a <em>Lücke</em> is expected to have a label.</p>

<h2 id="templates">Which of our layouts suit it</h2>
<p>The date-column layouts are closest to the tabellarisch convention: <a
href="../templates/ledger-resume-template.html">Ledger</a> puts the dates in their own left
column, and <a href="../templates/milestone-resume-template.html">Milestone</a> does the same
with a timeline rule. Both take a photo in the header. For a sidebar layout with room for
<em>Kenntnisse</em> and languages, <a href="../templates/aster-resume-template.html">Aster</a>
or <a href="../templates/halden-resume-template.html">Halden</a> work well.</p>

<h2 id="photo">About the photo</h2>
<p>If you include one: taken by someone competent against a plain background, business
clothing appropriate to the field, facing the camera, recent. A cropped holiday photograph is
worse than no photograph. Passport-style rigidity is not required — a professional
<em>Bewerbungsfoto</em> is a normal thing to pay a photographer for, and it shows.</p>
<p>And you are entitled to leave it out. The AGG means an employer cannot require it, and in
international companies in Berlin, Vienna or Zurich the anonymous application is increasingly
ordinary.</p>
''',
)
