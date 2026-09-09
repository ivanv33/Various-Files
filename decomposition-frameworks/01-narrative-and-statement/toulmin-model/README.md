# Toulmin Model

> Takes one argument apart into claim, grounds, warrant, backing, qualifier and rebuttal, so that the unstated rule carrying the evidence to the conclusion, and the conditions under which it fails, are made explicit. Category: Narrative & Statement Decomposition. Reference: [Stephen Toulmin](https://en.wikipedia.org/wiki/Stephen_Toulmin). [Open the 3D graph](./index.html) (needs internet for Three.js; on GitHub open via Pages or clone).

## What it decomposes

Toulmin's *The Uses of Argument* (1958) describes how practical arguments run, as against the syllogism. Its object is one argument: a claim and the case made for it. Grounds are the facts appealed to; the warrant is the general rule licensing the step from grounds to claim; backing is the field-specific assurance behind the warrant; the qualifier is how strongly the claim is held; the rebuttal is the conditions under which the warrant does not carry the claim.

It forces into the open the two parts speakers omit: the warrant, obvious to the speaker and open to challenge once stated, and the rebuttal, which an honest argument names and most do not. Without it an argument is a list of points and a conclusion, taken or left wholesale; the hosts below answer a well-made one with "That's a really good point. I haven't considered that." Decomposed, it shows one unstated rule doing all the work, one exemplar standing for a class of counterparties, and a rebuttal another guest supplied without anyone connecting it. Each unmanaged exception is an unpriced risk, which makes the rebuttal the idea-bearing slot.

## The slots

```mermaid
flowchart LR
  G((Grounds)) -- "supports (so)" --> C[Claim]
  W{Warrant} -- "licenses (since)" --> C
  B((Backing)) -- "backs (on account of)" --> W
  Q[/Qualifier\] -- "qualifies (presumably)" --> C
  R{Rebuttal} -- "rebuts (unless)" --> C
```

| Slot | What goes here | Typical provenance | Why that provenance |
|---|---|---|---|
| Claim | The assertion to be accepted. | either | Usually stated; a narrow stated claim often serves a broader implied one. |
| Grounds | The specific facts offered for the claim. | fact | Invented grounds mean no argument to decompose. |
| Warrant | The general rule licensing grounds to claim. | derived | Almost never stated; its confidence is the argument's real strength. |
| Backing | The assurance behind the warrant, not the claim. | either | Stated under challenge; the principle making it relevant is inferred. |
| Qualifier | How strongly, for what population, the claim holds. | derived | A hedge is a fact; the strength earned is inferred. |
| Rebuttal | Conditions under which the warrant fails ("unless"). | derived | Speakers rarely name exceptions; that another speaker's point is one is an inference. |

## Example 1: Harry was born in Bermuda

Toulmin's own textbook case, written as a short scenario so that facts can quote it; the rule that does the work is never stated.

### Source text

> At the passport office a clerk is asked whether Harry may hold a British passport. The file shows one relevant fact: Harry was born in Bermuda. The clerk writes on the form: so, presumably, Harry is a British subject. When Harry's employer asks why a birthplace should settle a question of nationality, the clerk replies that the office relies on the relevant statutes and other legal provisions, and that the presumption would not hold if both of Harry's parents were aliens at the time of his birth, or if Harry has since become a naturalised citizen of another country. The employer points out that nobody has checked the parents' nationality, and the clerk agrees to hold the passport until the birth record is examined.

### Decomposition

Grounds

- `g` **Harry was born in Bermuda** [fact] Harry was born in Bermuda. "Harry was born in Bermuda" (sentence 2, the file)

Claim

- `c` **Harry is a British subject** [fact] Harry is a British subject. "Harry is a British subject" (sentence 3, the clerk's note on the form)

Qualifier

- `q1` **Presumably** [fact] The claim is held presumptively, not with certainty: the clerk writes 'so, presumably'. "so, presumably, Harry is a British subject" (sentence 3, the clerk's note on the form)
- `q2` **Strength tracks the exceptions** [derived 0.60] 'Presumably' encodes that the two exceptions are rare but unverified: the claim is strong in the absence of evidence about the parents, and would become certain only once both exceptions are excluded. Rationale: Reads the stated qualifier against the stated exceptions. The text gives the word 'presumably' but not what strength it encodes or what would raise it to certainty.

Warrant

- `w1` **Born in Bermuda, generally British** [derived 0.90] A person born in Bermuda will generally be a British subject. Rationale: Nowhere stated. It is the general, bridge-like rule that alone carries the step from the birthplace to the nationality claim; the employer's question (why should a birthplace settle nationality) is exactly a demand for it.

Backing

- `b1` **Office relies on the statutes** [fact] The office relies on the relevant statutes and other legal provisions. "the office relies on the relevant statutes and other legal provisions" (sentence 4, the clerk's reply)
- `b2` **Statutes confer nationality by birth** [derived 0.75] The statutes make birth in a British territory such as Bermuda a ground of British nationality, subject to listed exceptions; that is why the birthplace rule can be relied on. Rationale: The clerk cites the statutes but not their content. The inference that they contain a birthright rule with exceptions is what makes the citation count as backing for the warrant rather than a bare appeal to authority.

Rebuttal

- `r1` **Unless both parents were aliens** [fact] The presumption would not hold if both of Harry's parents were aliens at the time of his birth. "if both of Harry's parents were aliens at the time of his birth" (sentence 4, the clerk's reply)
- `r2` **Unless naturalised elsewhere** [fact] The presumption would not hold if Harry has since become a naturalised citizen of another country. "if Harry has since become a naturalised citizen of another country" (sentence 4, the clerk's reply)
- `r3` **Parents' nationality unchecked** [fact] Nobody has checked the parents' nationality. "nobody has checked the parents' nationality" (sentence 5, the employer)
- `r4` **Alien-parents exception is live** [derived 0.70] Because the parents' nationality has not been checked, the first exception cannot be ruled out; the claim should stay presumptive until the birth record is examined. Rationale: Combines the stated exception with the stated gap in the file. The text says the passport is held until the record is examined but does not say which exception is the live one.

Edges. Four are facts, each quoting the scenario's own connective:

- `ce1` `g` -> `c` (supports) [fact] "so, presumably, Harry is a British subject" (sentence 3)
- `ce8` `q1` -> `c` (qualifies) [fact] the same span, read for its modal word (sentence 3)
- `ce12` `r1` -> `c` (rebuts) [fact] "the presumption would not hold if both of Harry's parents were aliens" (sentence 4)
- `ce13` `r2` -> `c` (rebuts) [fact] "or if Harry has since become a naturalised citizen of another country" (sentence 4)

Twelve are derived. Five carry a framework relation: `ce2` `w1` -> `c` (licenses, 0.90), rationale "The rule is the only thing that licenses the birthplace-to-nationality step."; `ce5` `b1` -> `w1` (backs, 0.85), rationale "The clerk offers the statutes in answer to the employer's demand for the rule; the text does not say the statutes contain the rule."; `ce6` `b2` -> `w1` (backs, 0.75); `ce9` `q2` -> `c` (qualifies, 0.60); `ce14` `r4` -> `c` (rebuts, 0.70). The other seven are grounding links: `ce3`, `ce4` from `w1` to `g`, `c` (0.90); `ce7` from `b2` to `b1` (0.75); `ce10`, `ce11` from `q2` to `q1`, `r1` (0.60); `ce15`, `ce16` from `r4` to `r1`, `r3` (0.70).

### What the LLM added and why it helps

With the derived layer hidden the graph is exactly the scenario. `w1` (0.90) is the rule the employer asked for and never got; without it the fact layer holds a birthplace and a nationality with nothing between them. `b2` (0.75) says what the statutes must contain for citing them to be backing rather than appeal to authority. `r4` (0.70) joins exception `r1` to gap `r3`. Derived edges: `licenses` from `w1` (0.90), `backs` from `b1` (0.85: the statutes were offered for the rule, not the claim), and `supported_by` from each inference to its sentence; the fact edges are the text's own "so", "presumably" and "would not hold if". The gain is a decision: the claim stays presumptive because one exception is unexcluded, and the record check would close it.

## Example 2: from the TBPN transcripts: Glenn Hutchins: the AI data-center build-out is not the CLEC bubble

Episode "Gemini 3 reactions, Cloudflare outage, the upsides of bubbles (Byrne Hobart, Glenn Hutchins, Yogi Goel, Sam Jones, Ali Madani, Amit Jain)", 2025-11-19, [transcript](../../../tbpn-transcripts/transcripts/2025-11-19_gemini-3-reactions-cloudflare-outage-the-upsides-of-bubbles-byrne-hobart-glenn-hutchins-yogi-goel-sam-jones-ali-madani-amit-jain.md); line numbers refer to it. Asked whether debt-financing AI infrastructure can be done responsibly, Hutchins agrees that it can (L4636) and then gives one complete argument in a single answer (L4640-L4886): a claim by disanalogy, five grounds, backing by credit rating and by the TSMC/Taiwan precedent (L4664-L4684), a self-supplied hedge, and a rule never stated yet carrying the whole step. The hosts do not contest it ("That's a really good point. I haven't considered that.", L4888-L4890); an earlier guest, Byrne Hobart, states the obsolescence condition that undercuts one ground (L3300), and Hutchins's involvement with CoreWeave, the exemplar he cites, makes the backing itself worth a Toulmin look.

### Facts (quoted)

Fourteen of the twenty nodes and seven of the thirty-two edges are facts, none of them paraphrases. Quotes keep the transcript's errors, such as "CLEX" for CLEC; `source_ref` is the speaker plus the line range in the file.

Claim

- `c1` **Not analogous to the CLEC overbuild** [fact] Today's AI data-center build-out is not analogous to the dot-com CLEC fiber build, where money went into the ground before the customers existed; it is a very different kind of financing structure. "it's not analogous. all to the CLEX where they put a bunch of money in the ground and then went to get the customers and the customer weren't there." (Glenn Hutchins, L4880-L4884)
- `c2` **Debt financing can be done responsibly** [fact] Financing the AI build-out with debt, Blue Owl-style, can be done responsibly. "It can be done responsibly, yeah." (Glenn Hutchins, L4636-L4636)

Grounds

- `g1` **Solvent counterparty takes all output** [fact] Almost every data center being built has a solvent counterparty contracted to take all of its output. "every one of these data centers, almost all of them, has a counterparty, a solvent counterparty that is contracted to take all the output." (Glenn Hutchins, L4790-L4798)
- `g2` **Built to suit, not build-and-hope** [fact] The data centers are built to suit a contracted customer, not on the 'if you build it, they will come' model. "They're built to suit, not if you build it, they will come." (Glenn Hutchins, L4800-L4802)
- `g5` **CLECs built first, went to zero** [fact] During the dot-com build the CLECs constructed fiber networks all around the country before the customers existed; they all went to zero and people lost their money. "the fiber optic networks were getting constructed all around the country, the CLECs, and those all went to zero and people lost their money on it." (Glenn Hutchins, L4772-L4780)
- `g3` **About 2x money over a 4-5 year deal** [fact] Each deal, so far as Hutchins understands it, generates about a two-times multiple of money over the four-to-five-year contract on the cost of buying the GPUs and standing up the data center. "in the four to five-year period of the deal, generates about a two-time multiple of money on the cost of buying the GPUs and standing up the data centers." (Glenn Hutchins, L4830-L4836)
- `g4` **Embedded option on used GPUs** [fact] After the contract the owner of the GPUs holds an embedded option on the value of the used GPUs, which will be worth something. "the owner of the GPUs in the data center has an embedded option, on the value of the used GPUs, which will be worth something." (Glenn Hutchins, L4852-L4856)

Warrant

- `w0` **Each build has a commercial case** [fact] Each contract and build has a commercial proposition in it; done well, as at CoreWeave, they stack like bricks in a wall. "each of the contracts and builds right now has a commercial proposition in it. And when done well, these companies that are doing this, like CoreWeave, are putting one of building a wall with one of those bricks on top of the other." (Glenn Hutchins, L4866-L4872)

Backing

- `b1` **Microsoft: best credit rating** [fact] Microsoft has, in Hutchins's view, the world's best credit rating, and will survive even if the sector collapses before it recovers. "Microsoft has, I think, the world's best credit rating." (Glenn Hutchins, L4810-L4820)
- `b2` **TSMC borrowed Taiwan's rating** [fact] TSMC succeeded largely because Taiwan was willing to lend it the national credit rating; capital at fab scale was only approachable that way, and the data-center build needs financing at a similar scale. "TSMC succeeded largely because the country of Taiwan was willing to, essentially, to lend them the credit rating." (Glenn Hutchins, L4664-L4684)
- `b3` **Old hardware keeps value** [fact] Used hardware keeps value: a five-year-old iPhone is still worth something even though people are buying the new ones. "I mean, your five-year-old iPhone is still worth something." (Glenn Hutchins, L4858-L4858)

Qualifier

- `q1` **Internet camp: some will fail** [fact] The claim is held in the '1999 internet' sense, not the '2008 subprime' sense: of course some companies will fail, some capital will be lost, and scoundrels will be attracted by the money moving around. "I am more in the internet camp which means that of course there will be companies that will be formed that won't be successful" (Glenn Hutchins, L4746-L4760)

Rebuttal

- `r0` **OpenAI burns capital first** [fact] The host notes how capital-consumptive OpenAI will be before profit or cash flow comes, unlike Google, which threw off cash well before its IPO. "you look at how capital consumptive Open AI will be before profit comes or cash flow comes" (Host, L4898-L4904)
- `r1` **Older GPUs can be worthless** [fact] A GPU that produces fewer tokens per watt than newer ones can be economically worthless even though it can still do something useful. "if the GPU is producing fewer tokens per watt and that just relative to newer ones, it can be economically worthless, even though it can still actually do something useful." (Byrne Hobart, L3300-L3300)

Fact edges. Seven, each joining two fact nodes and quoting the turn in which Hutchins states the connection itself.

- `e1` `g1` -> `c1` (supports) [fact] "but the major difference between that and today is every one of these data centers" (Glenn Hutchins, L4788-L4790)
- `e2` `g2` -> `c1` (supports) [fact] "the major difference between that and today is every one of these data centers, almost all of them, has a counterparty, a solvent counterparty that is contracted to take all the output. They're built to suit, not if you build it, they will come." (Glenn Hutchins, L4788-L4802)
- `e3` `g5` -> `c1` (supports) [fact] "The major difference between that, and people use that as analogy today" (Glenn Hutchins, L4782-L4784)
- `e4` `g3` -> `c1` (supports) [fact] "And the last point I would make and just finish this in a new one is that each of these deals" (Glenn Hutchins, L4826-L4826)
- `e5` `g4` -> `c1` (supports) [fact] "And then the owner of the GPUs in the data center has an embedded option, on the value of the used GPUs, which will be worth something." (Glenn Hutchins, L4852-L4856)
- `e6` `w0` -> `c1` (licenses) [fact] "So it's not, it's not analogous." (Glenn Hutchins, L4880-L4880)
- `e20` `q1` -> `c1` (qualifies) [fact] "I am more in the internet camp which means that of course there will be" (Glenn Hutchins, L4746-L4750)

### Decomposition

Six derived nodes fill the slots Hutchins left empty, and twenty-five derived edges carry every link he did not state himself. Fact nodes are referenced by id above.

Warrant (`w0` is the stated one)

- `w1` **Contracted offtake shifts demand risk** [derived 0.80] If a solvent counterparty has contracted to take all of a data center's output, the demand risk that sank the CLECs sits on that counterparty's balance sheet, so the build can be financed like a leased asset rather than a speculation. Rationale: Never stated. It is the only general rule that carries 'solvent counterparty contracted to take all the output' and 'built to suit' across to 'not analogous to the CLECs'. Contestable: it holds only while the counterparty stays solvent for the whole contract term. Supported by `g1`, `g2`, `w0`.
- `w2` **2x plus residual value bounds the loss** [derived 0.70] If a four-to-five-year contract returns about twice the capital and the hardware keeps resale value afterwards, the downside of each build is bounded even if AI demand cools. Rationale: Hutchins gives the 2x multiple and the embedded option as data but never says why they make the build safe; the bridging rule is that contracted cash flows plus residual value bound the loss. It depends on the contracts performing and on used GPUs holding value. Supported by `g3`, `g4`.

Backing (`b1`, `b2` and `b3` are the stated ones)

- `b4` **Project finance on offtake** [derived 0.70] Lending against contracted offtake rather than merchant demand is the standard project-finance structure for pipelines and power plants; a strong balance sheet behind the offtake is what makes capital-intensive builds bankable. Rationale: Hutchins invokes a financing structure and a credit-rating backstop (Microsoft, TSMC and Taiwan) but never names the project-finance principle that makes those assurances relevant to the warrant. Field knowledge, not stated in the transcript. Supported by `b1`, `b2`.

Qualifier (`q1` is the stated one)

- `q2` **Holds for hyperscaler offtake** [derived 0.65] The claim holds in aggregate for builds whose offtaker is a hyperscaler-grade credit; it is weaker for builds contracted to labs or neoclouds whose solvency depends on continued fundraising. Rationale: Hutchins's backing is a single exemplar (Microsoft) and his grounds say 'almost all', not all. Bounding the claim to counterparty quality follows from what he offers and from the host's remark about OpenAI's capital consumption. Supported by `g1`, `b1`.

Rebuttal (`r0` and `r1` are the stated ones)

- `r2` **Unless offtaker credit is weak** [derived 0.65] Unless the contracted counterparty is not Microsoft-grade: a large share of offtake is contracted by OpenAI and other labs that burn capital for years, so the 'solvent counterparty' premise depends on their continued funding. Rationale: The host observes that OpenAI will be capital consumptive before cash flow comes; Hutchins's solvency backing names only Microsoft. If the offtaker cannot pay through a downturn, the warrant's transfer of demand risk fails. Supported by `r0`, `g1`. Carries an `idea` field, quoted under "Where the opportunity shows up".
- `r3` **Unless used GPUs lose value** [derived 0.55] Unless the residual value of used GPUs is far below what the 2x math assumes: nobody prices the embedded option, and a newer chip that produces more tokens per watt can make an older fleet economically worthless while it still runs. Rationale: Hobart's economic-obsolescence point, made earlier in the same episode, contradicts the iPhone analogy; the deal math Hutchins cites is stated 'so far as I understand it' and depends on this unpriced option. Supported by `r1`, `g4`. Carries an `idea` field, quoted under "Where the opportunity shows up".

Derived edges. Twelve carry a framework relation; the other thirteen are the grounding links listed after them.

- `e7` `w1` -> `c1` (licenses) [derived 0.80]
- `e8` `w2` -> `c1` (licenses) [derived 0.70]
- `e14` `b1` -> `w1` (backs) [derived 0.80] Rationale: Hutchins offers Microsoft's credit rating immediately after the counterparty grounds ('If you sign a deal with Microsoft to take the off-put for your data center', L4812-L4812), but the warrant it backs is never stated, so the judgment that it backs w1 is inferred.
- `e15` `b2` -> `w1` (backs) [derived 0.70] Rationale: The TSMC and Taiwan story is told as the historical template and tied to the present with 'Very similar today, which is the scale of financing that's required to build all these' (L4684-L4684); that it backs the unstated counterparty warrant is inferred.
- `e16` `b3` -> `w2` (backs) [derived 0.60] Rationale: The iPhone line ('I mean, your five-year-old iPhone is still worth something.', L4858-L4858) follows the embedded-option grounds directly; that it backs the unstated residual-value rule w2 is inferred, and the analogy is contestable.
- `e17` `b4` -> `w1` (backs) [derived 0.70]
- `e21` `q2` -> `c1` (qualifies) [derived 0.65]
- `e24` `r0` -> `c1` (rebuts) [derived 0.60] Rationale: The host raises OpenAI's capital consumption as a contrast, not as an objection; reading it as an exception condition is an inference.
- `e25` `r1` -> `c1` (rebuts) [derived 0.60] Rationale: Hobart was answering a different question earlier in the episode; the judgment that his point undercuts the embedded-option grounds is the LLM's.
- `e26` `r2` -> `c1` (rebuts) [derived 0.65]
- `e29` `r3` -> `c1` (rebuts) [derived 0.55]
- `e32` `c1` -> `c2` (supports) [derived 0.70] Rationale: The CLEC disanalogy is the argument Hutchins offers for why debt financing can be done responsibly; he does not state the link.

Grounding links, every one a derived `supported_by` edge: `e9`, `e10`, `e11` from `w1` to `g1`, `g2`, `w0` (0.80); `e12`, `e13` from `w2` to `g3`, `g4` (0.70); `e18`, `e19` from `b4` to `b1`, `b2` (0.70); `e22`, `e23` from `q2` to `g1`, `b1` (0.65); `e27`, `e28` from `r2` to `r0`, `g1` (0.65); `e30`, `e31` from `r3` to `r1`, `g4` (0.55).

### What the LLM added

Inside the argument, `w1` and `w2` state the rules that carry five grounds to the claim (`licenses`, 0.80 and 0.70), `b4` names the project-finance principle that makes a credit rating relevant to a warrant about demand risk (`backs`, 0.70), and `q2` bounds the claim to the population the backing covers (`qualifies`, 0.65). Hidden, they leave a faithful but inert fact layer; shown, each rule can be asked whether it holds for a given data center and offtaker.

The three `backs` edges out of the stated backings are derived as well (`e14` 0.80, `e15` 0.70, `e16` 0.60). Microsoft's rating, the TSMC precedent and the iPhone line are all quoted, but the rules they are offered for are never spoken, so attaching each assurance to a warrant is the LLM's judgment, not the speaker's: a fact edge would need both endpoints stated and the connection quoted. The confidences track how directly the assurance follows its grounds, from Microsoft named in the same breath as the counterparty (0.80) down to the iPhone analogy standing in for the residual value of accelerators (0.60).

From outside the passage, `r0` and `r1` are facts with derived `rebuts` edges: the host offered OpenAI's capital consumption as a contrast, not an objection (0.60), and Hobart was answering a different question in an earlier segment (0.60). `r2` and `r3` restate them as "unless" conditions (0.65, 0.55), and `c1` supports `c2` (0.70) records that the disanalogy was Hutchins's answer to whether debt can be done responsibly, a link he implies rather than states.

### Where the opportunity shows up

The idea-bearing slot is the rebuttal (`idea_bearing_slot: "rebuttal"`): each derived exception is a condition under which the financing argument fails, and where the argument is acted on at scale an unmanaged failure condition is an underserved need. Two nodes carry an `idea` field.

- `r2` **Unless offtaker credit is weak**, derived, confidence 0.65. Idea: "A counterparty-risk rating or insurance product for compute offtake contracts, priced per offtaker and term, that lenders financing data centers could underwrite against." Read from the node: the solvent-counterparty premise that does the argument's work is untested for the labs and neoclouds that fund offtake by raising capital, and nobody rates or insures that risk.
- `r3` **Unless used GPUs lose value**, derived, confidence 0.55. Idea: "A priced residual-value benchmark or guarantee market for used accelerators, the analogue of the residual curves that make car leasing financeable." Read from the node: the 2x math carries an embedded option on used GPUs that nobody prices, and Hobart's tokens-per-watt point says it can go to zero while the hardware still runs.

Both sit in the 0.50-0.65 band, plausible but contestable, and for the same reason: each joins speakers who never addressed each other, and `r3` also rests on a number Hutchins gives only "so far as I understand it". `q2` (0.65) carries no `idea` field but frames the same opening from the qualifier side: the distance between "almost all" and "all" is the market.

## Building a knowledge graph with this framework

### Node and edge types

Node types are the six slots; one argument is one connected component headed by one or two `claim` nodes, and a segment arguing several claims gives several components that may share grounds. Edges: `supports` (grounds to claim; also a stated claim to the broader claim it serves, `c1` to `c2`), `licenses` (warrant to claim), `backs` (backing to warrant, never to a claim), `qualifies` (qualifier to claim), `rebuts` (rebuttal to claim as the registry defines it; Toulmin hangs it off the qualifier, recoverable through `qualifies`), `supported_by` (derived to fact, always derived). Facts carry `source_quote` and `source_ref`, derived nodes `confidence` and `rationale`; `entities` use the transcript extractions' spellings. An edge is a fact only when both endpoints are fact nodes and one turn states the link in words that can be quoted, so a `backs` edge pointing at an unstated warrant is derived however plainly the backing itself was said (`e14`, `e15`, `e16`).

### Fact or derived: rules of thumb

- Claim: extracted when stated, which is usual (the sentence with the "so"). Inferred when a narrow stated claim serves a broader one never said (`c1` stated, its link to `c2` not); worth it because the broad claim is what a decision rests on. Empty: description, not argument; skip.
- Grounds: extracted, always; a ground without a quote is an invented fact. Empty: keep the claim, leave grounds empty, lower the warrant's confidence.
- Warrant: inferred, almost always, as a general conditional that would carry any similar grounds to any similar claim; a restatement of these grounds and this claim is not one. Worth it because it is the contestable part and its confidence is the argument's honest strength. Extracted only when the speaker gives the rule (`w0`, weaker than the rule the argument needs).
- Backing: extracted when the speaker cites an authority, precedent or number for the rule; inferred, flagged as field knowledge, when the citation needs a principle to be relevant (classic `b2`, tbpn `b4`). The `backs` edge is a separate judgment: when the warrant it points at is derived, the edge is derived too, and its confidence records how directly the assurance was offered for that rule. Empty: lower the warrant's confidence; do not supply backing the speaker did not offer.
- Qualifier: extracted from hedges ("I think", "almost all", "presumably"); inferred for the population the claim actually holds for, usually narrower, because that gap is where over-generalisation hides. Empty: the claim is held as certain; derive a qualifier if the grounds do not support that.
- Rebuttal: extracted when the speaker says "unless", or when another speaker in the same source undercuts a ground (`r1`: fact node, derived `rebuts` edge). Inferred as the "unless" form of every ground and backing the argument depends on; worth it because it is the idea-bearing slot. Empty almost always, and that emptiness is the finding.

### Extraction recipe

```text
Decompose ONE argument from <file>, lines <a>-<b>, with the Toulmin model.
1. Claim: the conclusion a speaker wants accepted (fact). If it serves a broader
   implied claim, add that as derived with a derived `supports` between them.
2. Grounds: each specific fact or number offered for the claim, as a verbatim
   span of 5+ words. No span, no node.
3. Warrant: the general rule "if <grounds of this kind> then <claim of this
   kind>" (derived; confidence = how much of the step it carries). A rule the
   speaker states is a fact warrant.
4. Backing: what the speaker cites for the rule (fact); the principle needed to
   make it relevant (derived, flagged as field knowledge).
5. Qualifier: any hedge, verbatim (fact); the population the claim holds for
   (derived).
6. Rebuttal: per ground and backing, the "unless" condition under which it stops
   carrying the claim (derived). Keep the rationale about why the inference
   follows and put the need or idea it implies in the node's `idea` field.
   Search the whole source for a speaker stating such a condition: fact node,
   derived `rebuts` edge, rationale on the edge.
7. Edges supports/licenses/backs/qualifies/rebuts with provenance. An edge is
   fact only if both endpoints are facts AND one turn states the link, quoted
   verbatim; everything else is derived with a confidence. `supported_by` from
   every derived node to its facts, always derived.
Output one graph.json example: nodes [{id, slot, label <=40 chars, text,
provenance, source_quote+source_ref | confidence+rationale, idea?, entities}],
edges [{id, from, to, relation, provenance, confidence?, source_quote?,
source_ref?, rationale?}], idea_bearing_slot "rebuttal".
```

Afterwards: `node _meta/validate.mjs <dir>` (quotes, paraphrase cap, derived-to-fact connectivity), then four checks it cannot do: every warrant is general, naming no speaker or company; no `backs` edge targets a claim; no edge is marked fact unless both endpoints are facts and its quote really contains the connective; every derived rebuttal traces through `supported_by` to the ground or backing it negates, or it is a counter-argument imported from nowhere.

### Failure modes

- Warrant restated as the claim ("the data centers are safe because they have solvent counterparties"). Guard: conditional form, no proper nouns; if it cannot be written generally, `licenses` gets a low confidence.
- Backing attached to the claim (Microsoft's rating `supports` the claim). Guard: `backs` is the only relation out of a backing node and must target a warrant.
- Rebuttal as counter-claim ("actually it is a bubble"). Guard: every rebuttal must be writable as "unless ..." and name the ground or backing it turns off.
- Invented grounds: a plausible number the speaker did not say. Guard: the validator's quote check; anything assembled across turns is `paraphrase: true`, within the 30% cap.
- Dropped qualifier: every claim certain. Guard: search for hedges first; if the grounds say "almost all", the claim is not about all.
- Over-confidence from one exemplar: one counterparty becomes a rule for all. Guard: warrant and qualifier confidence track the number and variety of grounds; one exemplar caps them (here 0.65 to 0.80).
- Cross-segment rebuttals recorded as facts about the argument (Hobart's point is a fact; that it rebuts Hutchins is not). Guard: fact node, derived edge, rationale on the edge.
- The business reading written into the rationale, so the inference and the opportunity cannot be told apart. Guard: the rationale says only why the inference follows from the quoted facts; the need or idea goes in the node's `idea` field, and only in the idea-bearing slot.

## Related frameworks

- [Pyramid Principle](../pyramid-principle/README.md): a conclusion and its pillars arranged for a reader; Toulmin asks whether the pillars carry it.
- [Dialectical Decomposition](../dialectical-decomposition/README.md): a whole position against its critique; Toulmin's rebuttal is a condition inside one argument, for when only one side has spoken.
- [Issue & Hypothesis Trees](../../02-strategic-and-business/issue-hypothesis-trees/README.md): hypotheses with falsification conditions are claims with rebuttals; the tree for many hypotheses, Toulmin for one argument's warrant.
- [Inversion & Pre-Mortem](../../03-engineering-and-cognitive/inversion-premortem/README.md): failure pathways for a plan; the rebuttal slot does the same for the argument behind the plan.

[Library root](../../README.md).
