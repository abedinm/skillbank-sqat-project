#!/usr/bin/env python3
"""
add_concept.py - close the two Concept gaps the marking scheme names explicitly.

The guidelines award 20% for Concept and ask, in these words:
  "Does the project have a clear target market or audience?"
  "Does the team demonstrate a thorough understanding of the need, problem or
   opportunity, including evidence of research into the need, problem or opportunity?"

The document had neither a target-market statement nor a single cited figure. This adds
both, plus a References subsection for the sources.

EVERY figure below was fetched from its source and confirmed to appear on the page by two
independent agents before being used. No statistic here is from memory.
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "make_test_plan.py")
t = io.open(P, encoding="utf-8").read()
before = t

# ---------------------------------------------------------------- evidence in 4.1
OLD_41 = '''    P(doc, "The problem matters because the cost is not distributed evenly. A learner who "
           "cannot pay does not learn slowly, they do not learn at all, while the skill "
           "they could have traded sits unused.")'''

NEW_41 = '''    P(doc, "The scale of the payment barrier is measurable. In the average Bangladeshi "
           "household's education budget, private tutoring is the single largest line at "
           "26 per cent, ahead of both fees at 20 per cent and books at 23 per cent, rising "
           "to about 31 per cent at secondary level [1]. Households carry the majority of "
           "the cost: 71 per cent of total education spending in Bangladesh comes from "
           "households, the highest share of any country UNESCO reports for South Asia, "
           "and the proportion of rural households paying for private tutoring rose from "
           "28 per cent to 54 per cent between 2000 and 2010 [2].")
    P(doc, "The population that would benefit is both large and, by definition, without "
           "income. Twenty-two per cent of Bangladeshis aged 15 to 29 are not in "
           "education, employment or training, and youth unemployment in that age band is "
           "8 per cent [3]. The World Bank puts the NEET count at about 12.6 million, of "
           "whom roughly 90 per cent are women [4].")
    P(doc, "The formal alternative does not reach them. Only 5 per cent of the Bangladeshi "
           "labour force has received any form of training, and just 1 per cent has "
           "undergone technical or vocational training of any kind [5].")
    P(doc, "The problem matters because the cost is not distributed evenly. A learner who "
           "cannot pay does not learn slowly, they do not learn at all, while the skill "
           "they could have traded sits unused. One figure makes the waste concrete: the "
           "highest unemployment rate of any education level in Bangladesh belongs to "
           "those who completed tertiary education, at 27.8 per cent [3]. The people with "
           "the most to teach are the least likely to be earning.")'''

# ---------------------------------------------------------------- 4.2 evidence
OLD_42 = '''    P(doc, "The solution is feasible for a student project because it needs no payment "
           "gateway, no third-party integration and no infrastructure beyond PHP and MySQL. "
           "The entire business rule set is expressible in seven tables.")'''

NEW_42 = '''    P(doc, "Teaching is not a cost the teacher absorbs. Two meta-analyses find that "
           "preparing to teach and then teaching a topic improves the teacher's own "
           "mastery: Kobayashi synthesises 28 studies and reports effect sizes of 0.35 for "
           "preparing to teach and 0.56 for teaching after preparation [6], and Leung "
           "finds a weighted mean effect of 0.43 on tutors' own achievement across 16 "
           "articles [7]. The member who teaches to earn a credit is not donating time; "
           "they are learning while they do it.")
    P(doc, "The solution is feasible for a student project because it needs no payment "
           "gateway, no third-party integration and no infrastructure beyond PHP and MySQL. "
           "The entire business rule set is expressible in seven tables.")'''

# ---------------------------------------------------------------- target market
OLD_43 = '''    H(doc, "4.3  Existing Solutions", 2)'''

NEW_43 = '''    H(doc, "4.3  Target Market and Audience", 2)
    P(doc, "The primary market is tertiary students and recent graduates in Bangladesh, "
           "aged roughly 18 to 26, who hold at least one teachable skill, want to acquire "
           "another, and cannot or will not pay cash for it. Bangladesh had 3,695,233 "
           "students enrolled in tertiary education in 2019 [8], and the gross tertiary "
           "enrolment ratio stood at 23.7 per cent in 2024 [9], so the pool is in the "
           "millions and growing.")
    P(doc, "The market is reachable. Internet use in Bangladesh reached 53.4 per cent of "
           "the population in 2024 [10], 88.4 per cent of individuals use a mobile phone "
           "and 64.4 per cent personally own a smartphone [11]. Young people are the "
           "densest part of that: globally 82 per cent of 15 to 24 year olds use the "
           "internet against 72 per cent of everybody else [12]. A browser-based "
           "application with no app-store dependency reaches this audience directly.")
    TABLE(doc, ["Segment", "Who they are", "What they get", "Priority"],
          [["Primary", "Tertiary students, 18-26, with a teachable skill and no spare cash",
            "Learn a skill without paying, by teaching one they already have", "1"],
           ["Secondary", "Recent graduates building teaching experience or a portfolio",
            "Practice, a review record, and credits to spend on their own gaps", "2"],
           ["Tertiary", "University departments and student societies",
            "A record of peer learning happening inside their own community", "3"]],
          widths=[0.95, 2.45, 2.3, 0.65], size=9,
          caption="Table 1. Target market segments.")
    P(doc, "The addressable opportunity is not hypothetical: the Bangladesh online "
           "education market was valued at USD 446.4 million in 2025 [13]. SkillBank does "
           "not compete for that spend. It serves the users that spend excludes.")

    H(doc, "4.4  Existing Solutions", 2)'''

# ---------------------------------------------------------------- competitors, with pricing
OLD_COMP = '''    P(doc, "Commercial tutoring marketplaces such as Preply, Superprof and italki solve "
           "discovery and scheduling well, and settle in cash. They address a different "
           "user: one who has money and wants to buy time. They do not help the user this "
           "project is for.")'''

NEW_COMP = '''    P(doc, "Commercial tutoring marketplaces solve discovery and scheduling well, and "
           "settle in cash. Preply charges the tutor 100 per cent commission on a first "
           "trial lesson and between 18 and 33 per cent thereafter [14]; Superprof charges "
           "the student a subscription of USD 49 per month simply to contact a tutor [15]. "
           "Both address a user who has money and wants to buy time. Neither helps the "
           "user this project is for, and the second actively prices out a student without "
           "income before any teaching happens.")'''

OLD_TB = '''    P(doc, "Time banking systems such as TimeRepublik and hOurworld are the closest "
           "analogue and share the credit mechanism, exchanging hours rather than currency. "
           "They are generalist community platforms rather than skill catalogues, and are "
           "not organised around a curriculum, a skill level or a teaching relationship. "
           "SkillBank narrows the same idea to peer skill teaching and adds the offer "
           "catalogue, the skill level and the post-session review that a learning context "
           "needs.")'''

NEW_TB = '''    P(doc, "Time banking is the closest analogue and shares the credit mechanism. A time "
           "bank is defined in the literature as a system of reciprocal exchange where "
           "services are traded in units of time rather than money [16], and hOurworld, "
           "one of the larger implementations, states the principle as an hour of one "
           "person's time being equal to an hour of anybody else's [17]. The model is not "
           "merely theoretical: a controlled 12-month evaluation of 116 time-bank "
           "participants against 114 comparisons found significantly better outcomes in "
           "the time-bank group [18]. What these systems are not is skill-catalogued. They "
           "are generalist community platforms, not organised around a curriculum, a skill "
           "level or a teaching relationship. SkillBank narrows the same mechanism to peer "
           "skill teaching and adds the offer catalogue, the skill level and the "
           "post-session review that a learning context needs.")'''

REFS = '''
    H(doc, "4.5  References for Section 4", 2)
    P(doc, "Every figure quoted above was taken from the source listed here and checked "
           "against the source page.", size=9.5, italic=True)
    BUL(doc, [
        "[1] S. D. Bhatta et al., Bangladesh Education Sector Public Expenditure Review, "
        "World Bank, January 2019, p.46 (BBS Household Income and Expenditure Survey "
        "2016/17).",
        "[2] UNESCO Global Education Monitoring Report team, Private education has grown "
        "faster in South Asia than any other region in the world, UNESCO, 2 November 2022.",
        "[3] International Labour Organization, ILO's call for empowering youth for decent "
        "work and sustainable development in Bangladesh, 12 August 2024 (BBS Labour Force "
        "Survey 2022).",
        "[4] World Bank, World Bank Helps 900,000 Rural Youth in Bangladesh with Better "
        "Employability and Entrepreneurial Opportunities, press release, 27 August 2023.",
        "[5] M. A. Khan, Situation Analysis of Bangladesh TVET Sector, Skills 21 Study, "
        "ILO Country Office for Bangladesh, August 2019, p.16.",
        "[6] K. Kobayashi, Learning by Preparing-to-Teach and Teaching: A Meta-Analysis, "
        "Japanese Psychological Research, vol. 61, 2019.",
        "[7] K. C. Leung, An updated meta-analysis on the effect of peer tutoring on "
        "tutors' achievement, School Psychology International, 2019.",
        "[8] UNESCO Institute for Statistics, Enrolment in tertiary education, all "
        "programmes, both sexes, Bangladesh, 2019 (SE.TER.ENRL).",
        "[9] UNESCO Institute for Statistics, School enrollment, tertiary (% gross), "
        "Bangladesh, 2024 (SE.TER.ENRR).",
        "[10] International Telecommunication Union / World Bank, Individuals using the "
        "Internet (% of population), Bangladesh, 2024 (IT.NET.USER.ZS).",
        "[11] Bangladesh Bureau of Statistics ICT Survey 2024-25, reported by Bangladesh "
        "Sangbad Sangstha, Bangladesh achieves near-universal digital connectivity.",
        "[12] International Telecommunication Union, Facts and Figures 2025: Youth "
        "Internet use, 15 October 2025.",
        "[13] IMARC Group, Bangladesh Online Education Market Size, Share, Trends and "
        "Forecast 2026-2034.",
        "[14] Preply, Preply commission model, Preply Help Center.",
        "[15] Superprof, How Does Superprof Work? Fees, Booking and Student Pass.",
        "[16] N. S. Azizan et al., Willingness, motivators and barriers to time bank "
        "participation: a scoping review of 30 studies.",
        "[17] hOurworld, Peace, Abundance and Sharing through Equality in Exchange, "
        "hourworld.org/index.htm.",
        "[18] S. Lu et al., Promoting Late-Life Volunteering With Timebanking: A "
        "Quasi-Experimental Mixed-Methods Study, Innovation in Aging, vol. 8, no. 7, 2024.",
    ], size=9)

'''

edits = [(OLD_41, NEW_41, "4.1 evidence"), (OLD_42, NEW_42, "4.2 peer-teaching evidence"),
         (OLD_43, NEW_43, "4.3 target market"), (OLD_COMP, NEW_COMP, "competitor pricing"),
         (OLD_TB, NEW_TB, "time banking evidence")]
for old, new, label in edits:
    if t.count(old) != 1:
        sys.exit(f"ABORT: {label} matched {t.count(old)} times")
    t = t.replace(old, new, 1)
    print(f"  added  {label}")

# References subsection goes right before the requirement specification heading
anchor = '    H(doc, "5.  REQUIREMENT SPECIFICATION")'
if t.count(anchor) != 1:
    sys.exit("ABORT: section 5 heading not found")
t = t.replace(anchor, REFS.rstrip() + "\n\n" + anchor, 1)
print("  added  4.5 references for section 4")

# every later table caption shifts by one, since the target-market table is now Table 1
for n in range(13, 0, -1):
    t = t.replace(f'caption="Table {n}.', f'caption="Table {n + 1}.')
t = t.replace('caption="Table 1. Target market segments."'.replace("Table 1.", "Table 2."),
              'caption="Table 1. Target market segments."')
print("  renumbered later table captions")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("\nconcept gaps closed")
