# Technology

**Date:** April 08, 2025
**Source:** https://podscripts.co/podcasts/tbpn-live/zuckerberg-on-metas-new-llama-4-jeff-huber-sheel-mohnot-leif-abraham-samuel-hammond-victor-perez-jai-malik-pratap-ranade

---

You're watching TVPN. It is Tuesday, April 8th, 2025. We are live from the Temple of

Technology, the Fortress of Finance, the Capital of Capital.

And today we are particularly in the Temple of Technology because we're doing a deep dive

on Meta's open source AI strategy, talking to you through the history of Llama and how

they built out that LLM and what their strategy is with it.

Also all the teams behind it.

There's some interesting internal dynamics.

Benchmarks hate this one simple trick.

Saturate your models apparently, that's the trick.

We will be as fair and balanced as we can about it.

No, we're excited about Llama.

Yeah, I mean, there's a lot to like,

there's a lot to be skeptical of, and there's a lot of uncertainty,

but we are going to bring out a surprise guest, Jeff Huber, who was not in the announcement

post but will be joining at 11.30 to break it all down.

But let's start with AI at Meta on X.

They post, today is the start of a new era of natively multimodal AI innovation.

Today, we're announcing the first Lama 4 models.

This dropped on the weekend.

Shout out to Zuck for grinding constantly.

You love it.

Lama 4 Scout and Lama 4 Maverick,

our most advanced models yet,

and the best in the class for multimodality.

Always funny when you say our most advanced model,

it's our most powerful iPhone ever

because if it was less powerful, you wouldn't release it.

Like everything you do should be superlative

in the context of your own business.

Anyway, it clearly did mark a step forward

and they nailed some other superlative news

because they had the industry leading context window

of 10 million tokens.

Of course, that means how much information

can you stuff into a prompt

and still get reliable results out?

Google took it up to one million tokens

and that was amazing.

You could upload a two hour podcast.

You could upload an entire TBPN episode,

start asking questions and it would be able to find things.

It was pretty good.

At least Jim and I saw some demos of them

picking needles out of the haystack.

Hey, I changed one word in this entire book. Can you go find it and it would do it very very cool

Uh bit of a debate online about what that means for rag retrieval augmented generation

Which is where you load up a bunch a bunch of documents into something that the llm can kind of process through

And there's a debate now about

Is does does large context windows, do they kill RAG?

Well, we're having Jeffrey Huber on from Chroma.

He's a RAG expert and has built vector databases.

And he will defend his position.

And I think he'll have some interesting takes.

They also launched Lama for Maverick.

That's a 17 billion active parameter model with 128 experts.

So these are a mixture of experts models.

So there's a little bit of internal routing to find,

you know, what neurons in the LLM need to be activated

to go after math or writing or poetry or whatever.

And then they also have image class,

best in class image grounding with the ability

to align user prompts with relevant visual concepts

and anchor model responses to regions in the image.

And so a lot of these models are going multimodal

so they can deal with images and text.

And that's very important because obviously we as humans

can process both images and texts.

So if you wanna make something that's human level

or AGI or even close to it,

you gotta be able to do everything that the human can do.

And so this is where it gets controversial.

They said we have unparalleled performance to cost ratio

with a chat version scoring ELO, 1,417 on LM Arena.

That's where all the chat bots battle

and humans score which ones they like.

Very controversial, people are saying that the results

don't tell the full story.

So we're gonna dig into that.

But first, I want to go to a- Who was it was saying that the results don't tell the full story. So we're gonna dig into that. But first, I want to go to a-

Who was it was saying that the vibes were way off?

I mean, Rune was talking trash about Lama

when it dropped initially.

Of course, he's pretty aligned with OpenAI.

I think everyone knows that at this point.

But Rune was saying, everyone was like,

oh, OpenAI is cooked because Lama's now open source.

And he tweeted just like, have you talked to that thing?

Like and it was this idea of like yeah who cares about like whether or not they have the same number of parameters

Or it's open source. It's like do you have a good experience actually chatting with it?

And that's where the vibes are off

But there has been more commentary about the vibes and we will get into that but first I want to hear from Zuck himself

We have a clip from Zuckerberg explaining

Meta's open source AI strategy. So we're going to play that and then we'll use that as the

backbone of this analysis to really kick off how he's thinking about open source AI at

Meta because it did kind of come out of left field with VR, the very closed source, clearly

going towards let's build a platform, let're very close source, clearly going towards,

let's build a platform, let's lock everyone in,

but took a very different tact.

And to be fair, some of the VR work is open source,

but, and they do want to build an ecosystem,

but they're being much more aggressive

about open sourcing in AI,

and there's a lot of good reasons for that.

Ben Thompson has broken that down and when we've seen Ben Thompson's made a very

convincing argument for their strategy. Yeah basically why open sourcing this

and just making it widely available for free will benefit their ad

business long term which is the real you know cash. It's a bad day to not be

commoditizing your compliments. That's right. You always want to be commoditizing your compliments,

but let's hear it from Zuck himself. Let's do it. Do we have my view?

Is that open source is a really important ingredient to having a positive AI future.

And that there are all these awesome things that AI is going to bring in terms of productivity gains

and creativity enhancements for people,

and hopefully it'll help us with research and things like that.

But I think open source is an important part of how we make sure that this benefits everyone

and is accessible to everyone.

It isn't something that's just locked into a handful of big companies.

At the same time, I actually think that open source is going to end up being

the safer and more secure way to develop AI. I know that there's sort of a debate today

about is open source safe? And I actually take the different position on it. It's not

only do I think it's safe, I think it's safer than the alternative of closed development.

And a realistic aim that we should hope for is that we use open source to basically

develop the leading and most robust ecosystem in the world. And that we have an expectation

that our companies work closely with our government and allied governments on national security.

So that way our governments can persistently just be integrating the latest technology and have

whatever it is, a six month advantage, eight month advantage on our adversaries.

And I think that that's, you know, I don't know that in this world you get a 10 year

permanent advantage, but I think a kind of perpetual lead actually will make us more

safe in one where we're leading than the model that others are advocating, which is, okay,

you have a small number of closed labs, they lock down development, we probably risk being in the lead at all, like probably the other

governments are getting access to it. That's my view. I actually think on both these things,

spreading prosperity for more evenly around the world, making it so that there can be more

progress and on safety, I think we're basically just going to find over time that open source

leads. Look, there are going to be issues, right It's like, we'll have to mitigate the issues,

we're gonna test everything rigorously, we do, we work with governments on all the stuff,

we'll continue doing that. But that's my view of kind of where the equilibrium,

I think, will settle out given what I know today.

I think it's fascinating looking back at that historical clip and seeing how incredibly front

and center AI safety was. And then you look at the llama four announcement today and no one's saying,

oh, well, like llama four is like not safe or we should be having a safety debate. It's all about

the benchmarks. It's like, it's not superhuman enough. It's not aggressive enough. And so we've

kind of blown past that. But again, I do think there is a good AI safety argument

to be had about open source.

And I think it's played out kind of like he said,

like it's kind of good that, you know, at the very least,

it's like when you open source something like Llama,

it very easily can get in the hands of a,

let's not go to paper clipping,

let's just go to, you know, fraud on your grandma, right?

Sending spam texts that are LLM generated,

so they're a little bit more convincing.

We haven't really seen an epidemic of that yet,

and there's been just as much economic force

towards preventing that type of spam and scams

that the open source, like the net impact, I think has still been positive.

You get plenty of small companies or kids who,

yeah, I have a GPU rig that I used to game on

that was my Christmas present,

and now I can fine tune llama and make some app

or deploy it really cheaply, and that's a net benefit.

And the scammers aren't really getting away.

Like I keep going back to the election, and it's very hard to make the argument that AI

swung the election.

Even though, I don't know, both parties would probably have used AI.

Or Zuck has been accused of doing that or being...

With the 2016 election, right?

Yeah.

But it's much harder to make, which is weird because it's more...

I just think it's funny.

I love that he takes the position generally that he's like, you know, it would just be I really think we should avoid having

Like a few big companies. Yeah, it's like very important technology social networking. Meanwhile meta controlling

You know 20% of the US digital ads, you know, not even including, you know social networking, which I'm sure

Is significantly higher.

And also just this idea of if you want to

put something on the internet, increasingly,

this idea of the open internet where everyone has a website

and they all have their own style guides

and it's all this chaotic, what do they call it?

Web 1.0, Web 2.0 or something, I don't know.

That independent web has really disappeared because of Meta's

power over it.

But I don't know.

It still makes sense.

And I think it makes more sense from a strategy thing.

He's kind of making some arguments that

sound good in theory, but maybe aren't fully motivated.

They're more motivated by just his business needs.

He's an absolute dog.

He wants to win.

I think his business needs are real.

I think they're valid.

No, there's two things that can happen simultaneously.

One, open sourcing llama and allowing anybody

to build on top of it and do what they want with it

is a net benefit for the world.

It also very clearly is highly strategic.

He's doing it because he wants Meta

to be a much bigger company in 10 years from today

than it is now.

Yeah, no, 100%.

But if you are trying to look like Mark Zuckerberg,

you gotta get on Bezel.

Go to getbezel.com.

Shop over 24,500 luxury watches,

fully authenticated in-house by Bezel's team of experts.

You know he's got a Cubitus, he's got a Patek,

he's got a Peugeot.

He's got pretty much all of them.

He's got everything, he's got it all.

And now's your chance to catch up to Zuck

by going big on Bezel.

So download the app too.

The Bezel app is fantastic, highly recommend it.

You can scroll, filter, find what you like,

create a little wish list, and then pretty soon

start knocking those down as you send wires off to get

the Holy Trinity watches.

Yeah, and I'm to have, uh,

we're going to have a quayton again this week to talk about the watch

industry's reaction to the tariffs, which has not been, uh, you know,

switcher lens specifically has been targeted.

But moving on to, uh, uh, the reaction to llama four, uh,

the headlines were generally glowing, uh, two mediums,

two new medium sized mixture of expert open models

that score well, and a third,

two trillion parameter behemoth is promised.

So they didn't launch that yet, they're still training it.

That should be the largest open model ever released.

And again, openness is spectrum here.

There's open weights where you can fine tune it.

There's fully open source where you can actually see the code and all the changes. There's open data, you can fine tune it. There's fully open source where you can actually see

the code and all the changes.

There's open data.

You can have the data open source that they trained it on.

And also this is open source,

but all the big tech companies are doing this funny thing

where they're like, hey, anyone can use this,

really anyone, except for if you have over a billion,

over like $500 billion in revenue or something like that.

And it's basically just to exclude the other big tech companies. And they don't care. you have over a billion, over like $500 billion in revenue or something like that.

And it's basically just to exclude

the other big tech companies.

And they don't care, they set it like right,

whatever Snapchat's revenue is or user base is,

they're like, if they have 10% less, you can use it.

Which is like, honestly amazing for a lot of entrepreneurs.

So it's cool, but it's very funny that they're like,

I would not actually gonna help my competitors here.

Evan might kick the bots off and be like,

oh, fair game now.

But it's funny because like the history of open source

has been like MIT license.

You can even just take this code

and just go and sell it immediately.

And if you can get someone to buy it,

you can make money off of it.

Now they are in, there's a whole variety

of open source licenses.

But anyway, Meta just got a huge jump.

This is from LM Arena from 1268 to 1417 and that puts them allegedly higher than OpenAI,

higher than XAI, but it was hotly debated as we'll get into.

And so there were a couple of takeaways here.

Lama4 released on Saturday.

The blog post, so they didn't launch the paper

and there's nowhere near the level of detail

from the Llama 3 paper in terms of transparency.

And so that's another aspect of open source

is sometimes people wanna know,

hey, what other algorithmic tricks did you come up with?

What are you coming up with?

There was interesting, one of the most fascinating leaks,

I guess you could call it,

from the Llama open sourcing process

was that they had a bit of code in there

that was just called do not blow up the power station,

or do not blow up the data center.

And basically what they realized was that

when they're training Llama, they're running,

they're pulling so much energy from the grid

that if they finish training run

and then the power consumption drops,

it will do something with the power substation

and the transformers and the data center

literally might explode or something like that.

So basically what they did was they just said,

hey, when we stop training and we're not doing

all the matrix multiplication and all the math that you need to do to crunch all these numbers down to create the weights

Just do random math just just just keep doing random math because that will keep at least the energy will be the same

Obviously, it's not efficient, but we need to like wind down the energy consumption slowly. So very funny

Yeah, it's like sprinting right like yeah, you're sprinting and then you try to just halt. Yeah completely

You know exactly and so the smallest Scout model is a hundred and nine billion parameters if you're sprinting and then you try to just halt completely. You want to slow down, you know, slower.

Exactly.

And so the smallest Scout model is 109 billion parameters.

And this cannot run on consumer-grade GPUs.

And there was this funny interaction between, oh,

what's his name over at Google?

He's an absolute legend.

I forget.

Anyway, one of the top, Jeff Dean.

Jeff Dean, he's like the greatest programmer in

history and someone was like, Oh, this is such a bummer. I can't run the new llama on my

consumer grade GPUs. And he was like, what are you talking about? Like, of course you

can't. And somebody was like, Oh, like, like Google, like GPU expert AI expert, like discovers

what it means to actually have a consumer GPU. Yeah, because the like whoever this was

clearly was talking about like an Nvidia gaming PC.

But I'm sure Jeff Dean's consumer rig

is probably like $50,000 because they're just like,

here Jeff, why don't you just take the best thing

of everything?

Even when you're training at home,

you want to be able to run this.

It costs as much as a house.

Yeah, exactly, exactly.

And so there's also this question

about the claimed context token window, they're claiming 10 million,

and it's certainly far above what the real context is,

but it might not actually be 10 million,

we're gonna get into this with Jeff,

but there's this question of when you zoom out

the context window and you get so big,

just like a human, if you're walking around a library,

you might have access to every book in the library,

but you can't actually recall all of that.

So LLM seemed to be, there's this debate right now

in this take that the really, really high context windows,

maybe you get fuzzier as you get lighter,

just like a human.

And so that's where something like RAG and search

and deep research from OpenAI,

like it is a big context model,

but really what it's doing is it's

like going searching a webpage that's maybe 10,000 tokens, compressing that down, finding

the key insight, quoting that in.

And so when you get a deep research report, it's not really that it's stuffing all of

it into one context window.

It's that it's doing this thing iteratively like an agent.

And then there was a...

A genetic search.

And then this is where it gets controversial.

So LM Arena, we talked about how they're scoring very high

But they used a special experimental version for LM arena, which caused the good score

That's not the version that was released this discrepancy forced LM arena to respond by releasing the full data set for evals

And it does very poorly on independent benchmarks like AI dir

And so now there's so many different benchmarks out there

that you can kind of game one or a few or the top ones.

But if someone comes up and says like,

oh, well, you're actually doing worse on Arc AGI.

It's like, well, you didn't get a chance

to fine tune on that.

So if you underperform,

like a truly breakthrough genius LLM

should just be better at every benchmark,

even my benchmark of tell me a joke.

And so, you know, it's tricky.

There's this game of like, we gotta rank

on the important benchmarks, but now there's such

a long tail that you can't really optimize for all of them.

And then there's an unsubstantiated post

on Chinese social media that we covered on Monday

that claims the company leadership pushed for training more aggressively to meet Zuck's goals.

But this was categorically denied by Metta leadership

and we should go into what Ahmad over at Metta is saying.

He says, we're glad to start seeing Lama 4

in all your hands.

We're already hearing lots of great results.

People are getting with these models.

That said, we're also hearing some reports of mixed quality

across different services since we dropped the models. As soon as they were ready, we expect

it'll take several days for all the public implementations to get dialed in. We'll keep

working through our bug fixes and onboarding partners. We've also heard claims that we trained

on test sets. That's simply not true and we would never do that. Our best understanding is that the

variable quality people are seeing is due to needing to stabilize implementations. We believe the LAMA 4

models are a significant advancement and we're looking forward to working with

the community to unlock their value. Yeah I think what's happening here is that we

are hitting the pre-training plateau as we've heard before we talked to Dwar

Keshe about this and and and that's like underwhelming and then at the same time everyone has such strong

opinions about all the foundation labs. Like you meet someone and it's like oh you're an

anthropic guy. Oh you're an XAI guy. Oh you're a Meta bull or whatever and so there's a lot

of emotions that go into these things. I think the correct frame of mind to evaluate Lama 4 in is

what will people do with this that they couldn't do

with a closed source model?

And so when Google open sourced their dream studio,

there were people that were able to fine tune that

and create those magic avatars,

which are now kind of the Studio Ghibli's,

where you could upload a couple of photos,

get a custom avatar of you looking like Superman

or something, and so what's cool about Lama 4

is that because it's open weights,

it's easy to fine tune, and also it's not from DeepSeek,

so it's a little bit less politically controversial,

but there's still a lot that you can do with it.

It doesn't run on consumer GPUs now.

I'm sure that won't be a problem.

I'm sure that people are gonna figure out

how to distill this and do a bunch of different things. And when

we go through the history of llama, we will talk about some of the ecosystem

that has actually cropped up and is exactly what Zuckerberg was describing

in that. You want to hear a joke from Meta AI? Please tell me a joke like

Theo von about Sam Altman. Sam Altman is the ultimate tech bro.

He's out here trying to make AI do all the work

so we can just sit around and think about how great we are.

I mean, I'm pretty sure his five year plan

is to invent a robot that makes avocado toast

and brings it to him while he's meditating

on a beach somewhere,

because that's the real dream, right?

Wow.

AGI has been achieved internally, externally, everywhere.

Hang it up, folks.

Quit your job.

AI is here.

That's brutal.

And to be clear, I'm not actually, it's not clear that,

I don't think Llama 4 is actually running on meta.ai yet.

I think you're probably using Llama 3.

These rollouts are always really staged.

And in fact,

Was that the style of Theo Von?

I thought I was listening to Theo Von.

Could have fooled me.

That is remarkable.

Was that a Theo Von quote?

It's remarkable how spot on that is.

You listen to Theo Von's comedy.

Making an avocado joke is like very 2012.

2012 coded.

Yeah, like 2018.

Hipsters are quirky.

Yeah, okay, we're fast though.

Anyway, so there are mixed quality reports

across different services using Llama 4,

and implementations should stabilize in a few days.

This is kind of common when they roll out these big new models.

They got to figure out how to run them on all the hardware, get them into the data center,

swap things over.

Like people say, oh yeah, switching an LLM, it is just one line of code, but there are

more things to it, especially on the performance side.

We've seen this with Studio Ghibli, like the GPU is melting, which I think we all believe

is real because how many times, I mean, this happened to be a bunch where I've said, hey, this make this image studio ghibli. It's just like hey, I stopped and it's like what?

No, like Instagram filters. Don't just stop halfway

But we talked we talked about this with Aidan. Yeah, or was it Aidan or no Swicks? Yeah, Rick's was saying

That the the models are already showing signs of needing rest. Right? Yeah. Yeah

Anyways, it's crazy and so

There's the there's a bunch more going on let's move through this so so there's there's a couple themes that are sticking out in the

discussion about

Metas llama for performance the big one is is

Just a general disappointment from the AI community, I think,

based around how much horsepower was going into this.

So the claim was that they trained

on 100,000 H100 GPUs.

Of course, Zuck and Jensen have done

the famous Jersey swap.

He's one of the biggest Nvidia customers.

He can get the best, he's not under any import restrictions.

There's really nothing stopping him.

And most importantly, potentially,

is the fact that Meta can really, really go full send

on the CapEx here because Zuck knows that,

hey, if Llama doesn't go anywhere,

we never, like, LLMs cap out, it's not important.

Yeah, we're gonna use those 100K H100s

to train the Reels algorithm better, or the new thing. That was the whole thesis out, it's not important. Yeah, we're gonna use those 100K H100s to train the Reels algorithm better.

Or the new thing.

That was the whole thesis behind.

Yeah, or at the very least, do our own Ghibli style.

Yeah, yeah, yeah.

I was thinking about this, like if I wanted to,

if I was like the PM at Instagram,

I would immediately implement the Studio Ghibli filter

and just send every Instagram user a Ghibli

of their most popular post

or of their profile picture.

Just pre-render it all, just batch them all,

and then send them and just say,

hey, do you wanna try the new filter?

And everyone would be like, this is amazing.

It would be this amazing viral moment.

They could definitely do that,

but it would be extremely expensive

from a inference perspective,

but they can probably afford it,

and it would be cool and delightful,

and I think they should do it.

Anyway, so despite having fewer resources,

DeepSeq claims to have achieved better performance

with models like DeepSeq v3

and there are some benchmarks where DeepSeq

is still outperforming Lama 4,

which you hate to see if you're duking it out

in the open source world.

Jan Lacoon stated that FAIR is working

on the next generation of AI architectures

beyond autoregressive LLMs.

And so this is a debate that we've been hearing for a while.

We probably scale is important, and we

need to continue to scale, and we

want to do big data center build outs.

But we also need new algorithms on top of those.

The poster suggests that Meta's leading edge is diminishing,

and that smaller open source models have

been surpassed by Quen, with Quen 3 is coming.

And then there's another debate about Meta's Lama 4

fell short, Scout and Maverick have been released

but are disappointing.

Meta's AI research lead has allegedly been fired.

The models use a mixture of experts set up

with a small expert size of 17 billion parameters,

which is considered small nowadays.

Despite having extensive GPU resources and data.

Meta's efforts are not yielding successful models.

And so I think that there's a debate about,

George Hotz was talking about this when GPT-4 launched.

It was a mixture of experts model,

and a lot of that is defined by the actual structure

of the chips and the interconnect

and what we talked about with LightWave.

Is that right? LightMatter? LightMatter?

Just this idea that, yes, you can have 100,000 GPUs, but if they're not networked together uh, light wave, is that light matter, light matter? Yeah. Um, just this idea that yes, you can have a hundred thousand GPUs,

but if they're not networked together really, really well, uh, you're,

maybe their memory constraint,

there's all these different parameters that can constrain you.

And so you wind up having to fractionalize your, your, your, your,

your LLM. Um, and that can be fine if,

if 17 billion is enough and, and, and, and you can route,

and there aren't any problems that require

multiple experts or bigger experts,

but clearly in this scenario,

a lot of people are disappointed.

And so someone said, they left me really disappointed.

You hate to be disappointed.

I mean, what's obvious is-

The free magical intelligence

that you achieved to be here.

Show some-

Show some-

Respect.

Show some respect for Zuck giving you something

that cost a billion dollars for free.

Something that you like it.

Three years ago would have been groundbreaking.

Yeah, but the expectations are extreme.

Yep.

They're spending almost as much as anybody on this.

And ultimately it's becoming clear that ability to spend

is not all that, you know, it takes finesse too.

Yep. And so it's like, okay, Med-Ec and. Yeah. ability to spend is not all that you know it takes finesse to you yeah and so

it's like okay meta can yeah and so people are people are joking I'd like to

see Zuckerberg try to replace mid-level engineers with llama 4 and one

commenter joke that perhaps Zuckerberg replaced engineers with llama 3 leading

to llama 4 not turning out well brutal another commenter suggests he might use

he might need to use

Gemini 2.5 Pro instead.

I love that people are just absolutely trash talking

with the most industry jargon here.

Oh man, this is more of like, you're llama four coded,

not Gemini 2.5 Pro coded.

It's like, guys, having too much fun.

Anyway.

Yeah, this one was even more brutal.

Somebody's saying that calling it a complete joke

and expressing doubt that it can replace

even a well-trained high school student.

Oh yeah, yeah.

I mean, in general, I think my takeaway is like,

you know, Lama 4 might be underperforming,

but you can't sleep on AI even for a minute.

There's a new model every day.

You can't sleep on AI innovation, but you can sleep on an even for a minute. There's a new model every day. You can't sleep on AI innovation,

but you can sleep on an eight sleep,

so go to eightsleep.com, nights that fuel your best days.

Turn any bed into the ultimate sleeping experience.

Use code TBPN.

So this was the debate that was popping up

from Sean who came on the show last week.

He says unpopular opinion right now,

but Lama's four 10 million token window

will finally actually end the long context versus rag debate that's

retrieval augmented generation but not the way that other guy is thinking and so

this was a very like I I'm gonna tell we're gonna talk to Jeff about this

because I was like hey you got to come on the show just to explain this but I

think what he's saying is that is that huge context window is not a perfect

substitute for RAG and RAG still might have a place in the future of AI, agent development,

AI implementation, but I'm excited to dig into this because I didn't fully understand

this post and I want to know more here.

Anyway, let's move on to another LLM eval that happened with stagehand.

The results are fascinating what LLMs can actually do consists

Can actually parse deeply nested structured data like a DOM document object object model an a11y tree

Which is like parsing a website basically and so this founder

Benchmarked llama for against other models and found that llama for came in maybe eighth

below GPT 4o mini

Below Claude 3.5 sonnet and below deep seek v3 and then Gemini 1.5 pro

2.0 flash are all higher

Yeah

And so at least from his benchmarking he thinks that you know given that this is the latest and newest product from Meta, it's underperforming stuff that's been on the market for a couple

months.

So not the best information.

Then there's actually an example here that from Vic that I thought was pretty good.

This is the clearest evidence that no one should take these rankings seriously.

In this example, it's super yappy and factually inaccurate and yet the user voted for Lama 4,

the rest aren't any better.

So this is what a LLM arena actually,

or LLM arena interface actually looks like.

So there's a prompt and then you see both of these,

you don't see the names of the models I believe,

but you have to pick which one you like more.

And so the question was,

what is the latest season of fortnight and

Claude 3.5 sonnet said fortnight chapter 5 season 2 titled myths and mortals is the current season it begins on March 8th

2024 and features Greek mythology theme with characters and locations inspired by Greek gods and legends then llama for maverick

Experimental says a super timely question fortnight seasons are very short-lived and they last about 12 days like yapping yapping yapping and

then it gets it wrong it says the current season is fortnight season og

also known as chapter 4 season 6 which i believe is like before chapter 5

obviously i don't know enough about fortnight to fact-check this but it

seems like it's wrong and then and then there's a bunch of emojis and so there's

a debate from LM Arena,

and they go on to write,

we've seen questions from the community

about the latest release of Llama 4 on Arena

to ensure full transparency.

We're releasing 2,000 head-to-head battle results

for public review, so anyone can go see these

and decide for themselves,

hey, did the folks at LM Arena get this wrong?

Or are they happy?

Early analysis shows style and model response tone

was an important factor demonstrated

in style control ranking,

and we are conducting a deeper analysis

to understand more.

Emoji control, because some people might just be voting,

oh, I like the emojis,

even though that's kind of taking you away from the facts.

Or they might just be like,

hey, I like a more verbose answer.

Yeah, some people want a super short answer.

Yeah, exactly, exactly.

So there's all these human biases that are coming in.

And at this point, we are in this qualitative,

like the OpenAI guy said, just talk to the model.

Figure out the vibe of the model.

People seem to like Claude Sonnet

and just the vibe of that model.

And so there's still more debate over company leadership

potentially blending test sets from various benchmarks during the post

training process meta has denied that allegation but there is a lot of debate

raging and Ethan Mollick says the llama for model that one LM arena is different

than the released version I have been comparing the answers from arena to the

release model they aren't close.

And so what he did was he looked at the actual results

that were posted on LMArina and then same query

on the Lama 4 model that was released

and this is evidence that they went to LMArina

with a separate model, which is controversial.

It's an aggressive.

I mean, it doesn't inspire trust. It's an aggressive. I mean it doesn't inspire trust.

It's an aggressive approach, Cotton.

Yeah.

But you gotta do it in tandem

with your marketing and things.

Yeah, I'm interested to see what Jeff thinks

about all this.

And so, Ahmad says,

seems like there was a lot of truth in this leak

from two months ago.

Llama 4 is beyond disappointing.

It's a model that shouldn't have been released.

And this is from probably blind or something.

Metagen AI organ panic mode. It started with Deep Sea V3, couldn't have been released. And this is from probably blind or something.

Metagen AI organ panic mode.

It started with Deep Sea V3 which rendered Lama 4

already behind in benchmarks.

Adding insult to injury was unknown Chinese company

with a 5.5 million training budget.

And there was that meme of Iron Man being like,

they built this with screws in a cave.

You have a trillion dollar budget.

But if you want to control your budget,

you got to go over to ramp.com.

Time is money, save both.

Easy use corporate cards, bill payments, accounting,

and a whole lot more all in one place.

And so, Jeff is going to be joining in just a minute.

We will run through some of the timeline

and break down what happened with Lama

and the development here.

The most interesting thing that I found when I was digging through the history of Lama

was the company's notable foray into large language models was an academic tool called

Galactica, which most people hadn't heard about.

That actually backfired months earlier.

The demo was pulled after only three days amid criticisms that it confidently generated

false information.

And if you remember GPT-3, like it was, you get some wild hallucinations out of that thing. demo was pulled after only three days amid criticisms that it confidently generated false information.

And if you remember GPT-3,

like it was, you get some wild hallucinations

out of that thing.

And so Meta's leadership was cautious at that point

as generative AI fever swept tech

and once ChatGPT came out and it became like,

customers want this, then they started to push forward.

And so there was a team at Meta's FAIR research lab

in Paris, I believe this is the one

Yann LeCun is involved in.

They were hard at work on large language model

they believed could compete.

Llama One was the fruit of that effort.

A set of models ranging from seven billion

to 65 billion parameters trained on a rich diet of text,

which of course they have because they have

every piece of text.

Not only do they have everything in the Facebook ecosystem,

but they also scrape every link that's shared to Facebook,

which is every link ever.

And so they have the entire internet scraped.

Unlike OpenAI's headline grabbing GPT-3,

Llama wasn't offered as a public chatbot or API.

Instead, its initial release,

in its initial release,

Meta made the model's weights available

on a case-by-case basis to academic researchers.

So you would just email them and say like,

hey, I'm at Stanford, like, can I have the weights?

And they'd say, sure.

And then of course that leaked immediately,

which is awesome.

So it was a non-commercial license.

So they would send you the weights,

and then you could mess around with it and test.

But then of course someone, it was quote unquote,

open research, not open source,

so you couldn't build a company

on top of it.

It was more like a research paper

with some downloadable code,

but this leaked onto the internet,

and then developers everywhere had their hands

on a GPT class model in raw form,

and so that spawned these fine-tuned models,

Alpaca and Vicuna, which are derivatives of llama,

I think they're related mammals. And so then people started fine-tuned models Alpaca and Vicuna, which are derivatives of Llama. I think they're related mammals.

And so then people started fine-tuning with instructions

and getting it more into a chat mode,

and then Llama became a product

that had close to a chat GPT-like experience.

And so I'm excited to talk to Jeff about this.

I'm not sure if he's in the template yet.

He's in the waiting room.

Let's bring him in.

Jeff, how you doing?

How's it going?

It's great. How have you been following?

Well, first, welcome to the stream.

Can you do a little introduction?

It's too eager.

But then I want to hear your reaction to the Lama 4 news,

how you're processing and what it means for your business.

For sure. Yeah. I'm Jeff Huber, the co-founder of Chroma.

We're working on retrieval for AI and broadly working with developers

kind of across the ecosystem

to build production systems with AI.

A lot of it is focused on business applications,

good old fashioned business process automation.

And so always super excited to see new

open source model drops.

Can we go to this post from Sean?

He says, unpopular opinion right now,

but Lama's 4,

10 million token window will finally, actually,

end the long context versus rag debate,

but not in the way that other guy is thinking.

What does he mean by that?

Yeah, yeah, for sure.

I think Silicon Valley has a tendency

to be extremely intellectually shallow.

This is both a strength and a weakness of the Valley to be clear.

And in our view, AI is not this like Deus ex machina, this like technical machine god,

you know, where all of the information of all times is always going to be in the weights of this model.

This is really just a new form of computing.

And so in the same way that we have a memory hierarchy in classic computers,

we have the CPU, RAM,

disk and network, we are also going to have

a similar memory hierarchy in language models.

And again, it already exists today.

We have the actual sort of transformer attention heads,

we have the context window, we have the retrieval system

and tool use, and these things have different trade-offs,

right, you think about kind of access speed, capacity and cost, there are trade-offs to all and these things have different trade-offs, right? You think about kind of access, speed, capacity, and cost,

there are trade-offs to all of these things.

You know, I think like, you know, saying something is dead,

like plays pretty well on Twitter.

I've actually gotten myself into some trouble where I,

some people were allegedly ship posting,

and not actually sort of sincere posting about this,

and I didn't know, right?

Because they're hard to tell tell like what's a shit post

and what isn't.

But you know, the bait is strong on Twitter.

And so what Sean is saying is actually that like,

we've all been, there's a certain class of people

who are like long context is all you need.

Again, these people are probably like 21 years old.

That's fine.

We love them, but they just haven't seen how like

real systems depend on trade-offs between speed, cost, and

accuracy. And 10 million tokens is not a panacea. You need to keep information outside of the context

window. You need to give developers and programmers control over what information is inside the

context window. Even these needle-in-a-haystack tests are not actually that representative of

real-world utility and reliability of long context windows

You know they mentioned in the training for llama for didn't even have passages that are longer than I think 250,000 tokens

It's anything 50,000 is just

Synthetic data is we're just made up is what Sean is saying is that like well what 10 million tokens is finally?

Context window for llama for is finally gonna put to rest is that long context windows are all unique

He's going you know the 10 million the 10 million context window length isama 4 is finally gonna put to rest, is that long context windows are all unique. He's going, you know, the 10 million context window length

is going to finally, hopefully, you know,

make people understand that like, no,

there are different things here

that are good at different things

and we can put them together to create a good system.

Should we emanitize the Eschaton?

I don't know how you knew that I was writing

about this this morning.

No, we absolutely should not.

Yeah, we absolutely should not. Yeah, we absolutely should not.

It's always been a trail of tears.

Let's not do that.

Yeah, you explained that to me a while back.

I had fun with that.

So let's talk about Lama4.

How should startups be thinking about Lama4 as a tool in the toolkit

against the other options that they have?

Yeah, I mean, I think like, you know, Twitter is equipped to, and research in general, right,

is equipped to sort of view state-of-the-art

as the only thing that matters.

And I think that actually, in many cases,

being first is overrated.

You know, we've seen, you know, going all the way back

to sort of the Slack and Teams charts,

where you've seen the famous chart,

Slack versus Teams, right? Distribution is incredibly important

as long as the incumbents can wake up and can catch up.

I would not bet against Zuck

and $100 billion of profit per year.

I think that Zuck also is, in some sense,

playing a different game.

Like he's not trying to build the very best

open source chat experience for consumers. with Zuxes, I think rightly

so, is that having an open source model, which is really good, is good for the ecosystem

and is good for meta.

Most businesses don't love using closed source models.

They want to use open source models for all kinds of reasons, privacy, security, continuity, cost.

You can build your startup on GPT-4 and it's amazing. And then there's a new version out

and opening IDeplicates the old version. And all of a sudden all of your prompts don't work the

same. And so open source models are going to continue to play an extremely important part

in the ecosystem. Now, obviously, the DeepSeek R1 launched a few months back. I totally took everybody from Surprise. You

know, I think we're still in the early innings of this stuff where like good ideas can come

from anywhere. And oftentimes good ideas do come out of the sort of group think, you know,

context of Silicon Valley, right? So, you know, but yeah, I wouldn't, I wouldn't bet

against that.

Do you think there's an opportunity to build a company like Red Hat in Linux,

but for LLM implementation on top of something like Llama? Or is that like a crazy idea that

doesn't really match to the modern foundation model landscape?

I mean, the bull case for Llama for Met meta is that it's actually more equivalent to how

meta open sourced its data center kind of layout and text back.

And that's the bull case for meta is actually in industry sort of forms around that and

becomes the standard, right?

That's sort of why, you know, what argument for why they did it.

In terms of like the Red Hat 4, you know,, I think that Red Hat 4 works well for operating systems,

but I don't think of an LLM as an operating system.

I think an LLM is much more like a CPU, right?

It's an information processing unit.

And so obviously it's a new thing.

It's not exactly like a CPU,

but yeah, I'd have to reason about that some more.

I'm not sure.

Yeah.

If you're running MetaAI, what would you do from here?

Not to put you on the spot or anything.

Yeah, to be clear, I'm not running Meta AI.

I've not received that job offer at all.

I think that you have to keep going.

You can't stop.

I think focusing on the business use cases

is pretty important.

I think focusing actually also on what developers

actually need and want out of models is also very important.

You see a lot of like model drops that come out,

but they don't actually provide the real hooks

and they do very well in the benchmarks, right?

They do very well on like kind of the public leaderboards,

but they don't actually provide the hooks

that developers need to do like good tool use

or reliable structured data output

or the practical stuff, right?

The developers actually want out of models.

And so like, if you want to create a groundswell

of developers that like love your tools,

like do the developer experience part,

like meet them where they are and like give them

all the hooks that they need and don't just stop at like,

hey, look, you know, we hit standard yard benchmarking,

aren't we special?

Yeah. Is there, is there a narrative here where

maybe they're trying to do everything all at once

and instead should focus on like llama is amazing at code or llama is the next version of llama five

is like all about tool use or super great at reasoning or just like the best at deep

research or just the best at image generation for example.

Like it feels like there's kind of a bifurcation of the market and maybe the opportunity is

actually to laser in on something

that's high value, but then let the other stuff kind of simmer out there amongst other

teams.

I mean, a focus is probably always a good lesson for all of us, right?

Do less and do it better.

And so presumably that's also true for Meta.

I think also, obviously, unlimited capital can both be a blessing and a curse in that

way. Yeah. Again,

like focus on developers. Developers want, I think that's the beach head.

That's how you win the B2B market.

If you win the B2B market with your open source models,

like you get all of the sort of downstream effects that you want. You know,

you don't need to beat, you know, GPT-5 on some bet.

Yeah. Do you think that part of the narrative that we're seeing around

llama four is just pre-training, scaling, hitting a wall, a need for new

algorithms, a need for a deeper focus on reasoning and maybe even

whatever comes after that?

I mean, you know, I, I, you know, so you mentioned a moment ago, sort of the,

you know, immunitizing the eschaton, right?

You know, right.

History, you know, every exponential that we've observed eventually

results in a sigmoid curve. Sigma. You're eschaton, right? You know, right? History, you know, every exponential that we've observed eventually results in

a sigma wave curve. You're never early COVID, right? The,

the fur of like, Oh my gosh, you know,

the Twitter guys doing their thing where they're like, well,

if, if double the amount of people get it every day,

then everybody on earth will have had it seven times.

The next 100 billion people will have it. Yeah, exactly. Exactly. Yeah.

And so, you know, I think that there are laws of physics here.

I think that there are, you know, um, diminishing, they're clearly diminishing marginal returns,

right?

We're spending 10x on compute.

We're not getting 10x or better models.

At least, evidently not yet.

And so, you know, the transformer is incredible, is amazing.

It's a, you know, technology is probably as important as the invention of electricity.

It will probably, you know, bring about a increase in GDP that is on the important as the invention of electricity. It will probably bring about a increase in GDP

that is on the order of the Industrial Revolution

or greater.

And so I think we should not minimize this technology

and sort of boil it down to, oh, this is sort of just dumb

pattern matching.

By the same token, we also should not

believe that all technology we're

going to be able to rent seek on forever.

So yeah, new things are definitely needed.

And I think that an an inference type compute,

internal change of thought is really promising.

And I look at the stack today

and I think about how sophisticated computers are, right?

And how good architectures are and operating systems

and kernels and compilers and all of this stuff.

And we're just like in the baby phase today of AI.

It's just in its infancy, there's a lot to build.

From a recruiting standpoint,

have you run into some of these super aggressive

non-competes that we're seeing?

There was a headline today about, you know,

Google basically paying engineers to not work at Chroma.

Not work for a year when, you know,

they could be working at Chroma or any of these other labs.

I mean, yeah, you know, airplane red dots.png, right?

I guess like if I was affected by that, I wouldn't know it.

So yeah.

Yeah.

Can you take us through some of what Chrome

is building today and where customers

are getting the most value?

I've talked to you a little bit about some

of the use cases and I think they're underrated potentially

in like how simple and obvious they are

when you explain them, but I want you to take me through some of the modern context. Yeah, I mean, you've heard left and

right on the internet now for like three years all about this acronym RAG. I don't know why

anybody would ever name something RAG. We just call it retrieval. And of course, the idea with

retrieval is that if you want to build an AI system and you want to be good at something,

well, you need to teach it how to do that.

You got to teach it about your data.

You got to give it your instruction set, right?

And updating the weights of the model

is not a very good idea

because you cannot really deterministically control that,

right?

You can fine tune,

but what you're going to get at the other end,

you know, again, you don't really control.

And so giving the system access

to a repository of instructions or knowledge

about your organization,

your business problems, that is something that you can control.

And that's the problem that retrieval solves.

And so, you know, we talked to enterprises and businesses building useful applications.

I think like today, 90 plus percent of it in enterprises is retrieval of generation

or it's using retrieval.

It's sort of chat on top of unstructured data.

You know, I think if you zoom out, though, and view what is really AI,

AI gives us the primitives and the ability

to process unstructured data in a common sense fashion.

And you think about the scale of data.

Even today, inside of enterprises,

unstructured data is 10 times the size of unstructured data.

We have 10 times more unstructured data.

And then you consider the real world.

If we were actually putting robots out in the real world, how much unstructured data

they're going to be ingesting and needing to process and reason about and action on.

It's just going to be 1,000x, 10,000x, 100,000x of data that we have today.

And so that's the direction.

I think it's not so much this simple one human, one AI talking in a chat stream

back and forth. But it's like real embodied intelligence, which, you know, you could call

an agent, you can call a robot, you know, I don't love any of these terms. But like,

really the goal here ultimately, I think for anybody who's building something practical,

is building something that's reliable. You know, you think about like, we've been seeing

self driving touted as like this technology for like 10 years. You think about, we've been seeing self-driving touted

as this technology for 10 years.

Of course, if you live in San Francisco,

you can use Waymo and it is actually incredible,

but it's taken 10 years.

The Gatsby demo and production has always been so great in AI.

If you're building something practical in AI,

your big question as a developer is,

okay, the demo is super sexy and cool,

but how do I actually make it work really well and reliably?

The ability for these systems to self-improve or improve under human guidance, super sexy and cool, but how do I actually make it work really, really, really well and reliably?

And the ability for these systems to sort of like self-improve or improve under human

guidance, I would say is like the biggest thing that's underrated today.

And of course, you know, we think that like retrieval plays a key part in kind of how

that happens.

Can you concretize that a little bit by walking me through like a potential use case for us?

I mean, we stream three hours a day.

We're probably emitting,

you know, I don't know, tens of thousands of tokens every day. If I used whisper, I

transcribe every minute of our show. I could search that through, you know, fuzzy search

or deterministic. If I want to just search like every time I mentioned artificial intelligence

directly find that, or I could try and fine tune Lama 4 on it and maybe it just hallucinates like,

Oh yeah, John was talking about this randomly.

How, how would I, how would I use Chroma to create a,

a more definitive index of every time John or,

or guest has talked about artificial intelligence or, or Lama in, you know, hundreds of hours of video.

Is that something you could do? Yeah. Yeah.

I've seen some like kind of fun things today where like, you know,

people are taking the corpus of all of their writing or all of their speech and

the kind of like quote teaching the model it,

they're loading it into a tool like chroma,

sure hooking up your language model and they're getting end users the ability to

like chat with John and like, John thinks about artificial

intelligence, right?

And that's exactly right.

So we've got all those transcripts get processed

to get broken into pieces, they get indexed

and searchable in various ways.

And then when the user asks the query,

Hey John, what do you think about the latest Lama release?

Or maybe they didn't say Lama,

they say the latest release,

the latest AI from Facebook thing right now.

Lama. Like the search is good enough that it can like find Or maybe they didn't say llama, they say the latest release, the latest AI from Facebook thing right there.

Yeah, exactly.

Lama.

Yeah.

Like the search is good enough that it can like find all the relevant things that you've

said and then the L can like respond as you because it can kind of ground itself into

the things that you said before.

So that's a-

Yeah.

And so it's basically taking like different blocks of text, different ideas, and then

kind of vectorizing them into some way that's not necessarily human readable, but it can

still- it's basically like better fuzzy search

in many ways, not to degrade what you're doing,

but it's amazing, it's magical and super powerful.

Fuzzy, yeah, fuzzy search is really useful

when people are not experts in their own data, right?

Is that if you're Google Drive,

you know how to search for stuff pretty well, right?

But like your users don't know how to search

for the stuff that you've said before.

And so that's the kind of the power of like embeddings

and vector search toolbox.

It's not a panacea again.

We're not monetizing the eschaton here.

We're not too panic, right?

But it was like a very powerful tool

and people are getting a lot of value out of it.

Yeah.

I'm curious your reaction to AI 2027.

Our point of view, generally,

just from all the conversations we've had,

is that like sort of model progress and advancements

could slow, and that would be fine,

just because there's so much value to unlock out

of the underlying models.

I'm clear.

I'm curious to think how you processed just the forecast

generally.

Maybe take it from there.

I mean, I think the capability overhang we have

in the models that we already have today,

and we will have absolutely in six months, is immense.

You think about, for example,

the possibility of democratizing access

to state-of-the-art services to everybody on Earth.

Like, it is very possible the poorest people on Earth today,

or in 10 years, will have access better health care, better legal representation,

better financial services than billionaires have today, I think that's entirely possible.

And that's impossible with the model that we have again today. And so the capability

to overhang is immense. Every time an extremely long essay from a sort of effective altruist drops,

it clearly tends to make waves.

I think if you tell people that the world is going to end,

they're going to pay attention.

And, you know, I'm just like not that frankly,

that interested in like secular eschatologies about,

you know, apocalypse in the end of the world, right?

Like, I think like there's a natural tendency

for all humans to believe that like,

we are the chosen ones living in the special time

and the last days, right? You know, even Fukuyama wanted to end history, right? And so,

natural human tendency, you know, this is again, the immunitizing, the eschaton, we'll mention it

three times now, it's really dangerous, right? Like, you think about what's happened throughout

the last hundred years in like really,

you know, the hundreds of million people that have died,

you know, across like different world wars

and different, you know, dictatorships.

Like it is oftentimes it's like messianic complex

that leads to a lot of that.

And so, I don't know, I'm just like,

I think it's, I see it as entertainment

more than anything else.

Yeah, thought exercise.

On a more practical note,

like I go to the Wall Street Journal's website,

I just try and search for an article and they say, oh, search is powered by AI.

It's not clear.

It's clearly not powered by AI because I cannot fuzzy search at all.

I can't say, oh, I know that it mentioned this person and I think it was about this

and it was in the last week.

It's not there.

What does it take to actually roll this stuff out?

Are these even potential customers of Chroma or is there another company to be built here?

What do you think about that?

Yeah, um, Wall Street Journal if you're watching, you know, send me an email

Yeah, all that's very doable today. I think that you know, the reality is that you know, you're classic, you know

The future is already here. It's just not evenly distributed yet, right? Like, you know any

Technology of consequence even if generationally important, you know, still takes decades to roll out.

And, you know, that's just the same just through here. So.

That's great. Well, thanks so much for stopping by. We got to move on,

but this was a fantastic conversation. We'll have to have you on again.

Thanks for coming on, Jeff.

I really appreciate it. Talk to you soon.

And we got a big funding announcement. We're shifting gears.

We're out of AI and into manufacturing.

Going to talk tariffs.

Going to talk industrialization, another theme

we love on this show.

We have some big news.

And I just want to know, was this fundraiser announcement

always intended to go out today?

Or did they bring it up?

Oh, because of the tariffs.

Because of the tariffs and everything.

Because the timing is just too good.

So Jay says, today I'm excited to launch

the advanced manufacturing company of America.

We've raised $76 million.

Let's hear it for a massive round coming out of stealth.

From Caffeinatedinated capital that's Raymond

Tonsing founders fund Lux capital and recent Horowitz and others the best

time to build this business is right now yeah no joke yeah but the real work

began decades ago and they just decided I'm gonna get every big fund yeah just

get them all yeah it's great in a He says yes to everyone. Take a bit from

everybody. And it's great. They put out a four minute video

produced by James Jason Carmen, story company. It's beautifully

lit, beautifully shot. And they brought in, you know, we've been

hearing for a long time that the legacy manufacturing companies

are run by folks who are aging out and maybe they don't have the next generation lined up

to take over the business.

Well, they sat down and they interviewed one of those folks

and it's a fantastic video, you should go check it out.

Anyway, is he ready to come on in the studio?

Let's bring him in and hear the news from him directly.

Welcome to the studio, how you doing?

Congratulations.

Hey, how are you guys?

We're fantastic, thanks so much for taking the quick moment

to chat with us.

Can you introduce yourself, the company,

and what's the news today?

Absolutely.

My name is Jay Malik.

I'm the CEO of the Advanced Manufacturing Company

of America.

We call it, affectionately, AMCA.

And so what we do is we design, manufacture, and certify

the next generation of critical products, uh,

that go into all aerospace and defense systems.

So that's both existing and new systems, you know,

the stuff that that Boeing makes, uh,

and the stuff that Andrew is going to make. Okay.

Can you break down a little bit more of like what the first products that you'll

make will look like? We've heard about what Hadrian's doing. We've heard about, you know, injection molding plastics.

Like there's a lot of different buzzwords. Obviously everyone kind of

wants to do everything in the long term, but what are you focused on first?

Yeah. So first let me, let me just throw a high level, right? Like when we talk

about the aerospace and defense frames like Lockheed or Boeing, um, they don't

make anything today, right? They've outsourced a lot of their manufacturing

and engineering to thousands of suppliers.

Some suppliers are focused on high volume manufacturing,

things like wire harnesses, machine parts,

with the hydrants during injection molding.

There's a lot of great suppliers that are focused on that.

But there are also hundreds of suppliers

that are focused on critical engineered products.

Those are the products that, you know,

basically determine system success

or failure and are often very, very highly specialized. So stuff like avionics products,

power units, specific engine products. And so we're focused in those areas, in the most critical

areas where you need to both engineer and manufacture at relatively low volumes for

the end customer for their system to succeed.

So we're focused on a pretty different, I would say part of the market compared to most

of the sort of software defined manufacturing startups that you often see today.

In terms of where we're starting, we're starting, you know, almost entirely on avionics, you

know, the part of the plane or the ground control system that involves, you know, controlling entirely on avionics, you know, the part of the plane or the ground control system

that involves, you know, controlling it, right? So the stuff you've seen a cockpit, for example.

It's more focused on things like switches, panels, displays, power units, you know, things that are

critical to the pilot if it's a manned system, and, you know, if it's an unmanned system,

critical to communication and executing on the mission.

So those are the areas that we're mostly focused on right now.

Can you talk about the timing of the announcement?

Was it just a happy accident you were always planning to go out this week or did you pull

it forward due to everything in the news?

A little minor news this week.

We were supposed to launch this week anyway,

but we actually had a few reporters

that I think got scared of the tariffs.

You know, it didn't want to cover anything.

And so we basically said,

I'm not sure if I'm allowed to curse on this podcast,

but F that.

And said that this is actually the best F in time

to like, you know, take our company public.

So we just did it.

And so yeah, it was planned,

but obviously timing is definitely in our favor.

Can you talk about, this is obviously a big raise

to come out the gates with, can you talk about, you know,

kind of the use of proceeds and kind of like,

I'm curious about kind of like how you're thinking

of the structure of the business generally.

Yep, so we're gonna be,

we've already acquired one business

that is a critical avionics supplier,

which you saw a video,

or some people may have seen a video about.

We're going to be acquiring probably another two

to three of them over the next 12 to 18 months.

We're also going to be doing our own clean sheet,

design and development of adjacent

products in this space with our own manufacturing and engineering talent. So it's a hybrid approach.

I'm a firm believer that especially in this area of the supply chain, you can't just hack your way

into it. You also can't just be a private equity firm and buy and price it up. You know, that's not going to achieve what

like, you know, companies like Andro want to achieve, you know,

for their customers. And so we're taking a hybrid approach

where we're buying, you know, companies with products that we

think are going to be hard, you know, to just redesign from

scratch, and also developing ones that we think we can do a

great job of ourselves.

And as part of your advantage over traditional private equity

is just the time horizon you're thinking about of saying,

we don't need to come in and just immediately cut costs

by 50% and increase pricing and hopefully flip

the business in three years.

I imagine you're buying to hold, and that's

part of why somebody would want to sell to you in the first

place, I imagine.

Yeah, it actually goes deeper than that.

So I would say the one thing that I have learned building this business so far, I believe it's

still early, is that owners don't really necessarily care just about the time-rise and your ability

obviously to underwrite the deal.

They also care about, one, not selling to MBAs, not selling to traditional finance people.

You'd be surprised.

It's a big thing for them.

And that second, that you know what you're doing, meaning like, you're not a bunch

of like search funders, you're not a bunch of people, except from the MBA argument,

but like you're not a bunch of people that haven't spent time in manufacturing,

shop floor, et cetera.

And so our entire team are engineering and

manufacturing folks, we spend our entire careers, you know,

designing things for SpaceX manufacturing things, you know,

we're also young, which I think people like to see when when

they're selling their business, they know that just looking, you

know, looking at the person across the table that they're

going to be there for that for the next 20 or 30 years. So say

all of those things combined

make it a pretty strong pitch for wine to sell to us.

Did you have this idea in mind or a rough idea of it

when you decided to go back, enter your next chapter?

I remember it felt like a year ago

when you decided to move on from active investing.

It felt like, I just remember that instantly you shared it

and it just was like everywhere.

And because people at that time,

it was like every non deep tech, hard tech investor

was like starting to pile into the category

and everybody's like, wait.

Wait, if he can't do it, I'm screwed.

What are we doing?

It didn't slow anything down obviously,

but I'm curious, like, you know, kind of the origin.

What am I doing getting in this region?

Yeah, I'm curious, like, how the idea and the opportunity

came together.

Yeah, so I spent three or four years, obviously,

my career at Countdown.

When I was 24 years old, I started the firm.

I spent a lot of time with many fashion startups

and also with mom and pop suppliers.

As part of my diligence for whether I should invest

in companies, I would talk to mom and pops.

And so I'd spend three or four years in the space

and it didn't really click, I think,

until after I shut down Countdown,

that one, the mom and pops have both the expertise

and in some cases, the qualifications that you need

in order to develop and manufacture

and bring the product to market.

And then it also didn't occur to me obviously

when I was venture investing that maybe there is a path

where you can combine the mom and pop advantages with the spirit,

the culture, the talent of a startup.

When you're venture investing three or four years

every single day, your mind is just like,

startup, startup, startup, new things, new things, new things.

You're not even able to think about

what does the future look like

using something that already exists.

And so it wasn't until I had actually shut down Countdown, had like a month and a half

to reflect, think about what I had learned, wrote down some key themes, and then you just

start to iterate from there.

Talk to people, talk to customers in the industry, talk to people at companies that are already

building very successful ones both in startup world and in mom and pop world.

That's when the vision started to come together.

Hey, I'm uniquely in the center of these two movements.

I helped, I think, start and invest in a lot of startups in this space.

At the same time, I know a lot of people who are in the traditional world, and I should

use that to the maximum advantage that I can.

I have one last question, and then I'll let you go,

because I know you're busy today.

Charlie Munger criticized Transdime

for buying aerospace parts manufacturers

and then locking Primes and aerospace companies

into long contracts, raising prices.

It was a little bit of a controversial strategy,

but it's performed very well for that company.

What is your takeaway from the Transdime model?

Transdime is actually a phenomenal business

and it's actually not the cause of any of those issues.

The cause of those issues, certification, lock-in,

et cetera, et cetera, has to do with decisions

that were made 30 years ago at

you know the top of Boeing which is a paper right here you know basically

pillorying that decision but the decision of the top of Boeing to outsource every

single thing that they do from from engineering and manufacturing at the

component and at part level up to the product level and so Transigm is just a

recipient of the system

that was instituted 30 years ago.

If you really want to change things,

we believe that you have to start from the bottoms up

with the critical products,

build your way back up in partnership with the customer

to reverse that type of decision making and culture.

So yeah, my answer to that is,

I think Transigm is actually a great business.

They have run businesses very, very well.

They are in an environment that was not created by them.

They have taken advantage of it, but it was not created by them.

And to fix that, it's going to take partnership with a company like Apps.

Well, that's a fantastic answer.

Thanks so much for hopping on on short notice.

Congratulations on the round and we'll have to have you back.

Yeah, I have so many other questions I want to ask.

We can talk for an hour, I'm sure. Yeah, very excited for you and the team and excited to have you back on the round and we'll have to have you back. Yeah, I have so many other questions I want to ask. We can talk for an hour, I'm sure.

Yeah, very excited for you and the team

and excited to have you back on the show soon.

Thank you.

Let's do it.

Take care, guys.

Talk to you soon.

Bye.

Well, we are moving on to someone from FAI,

the Foundation of American Innovation, I believe

is what they call it, FAI.org, the FAI.org.

I've been to a couple of their events, very fun.

Gary Tan spoke at one, Trey Stevens spoke at one.

Yeah.

Trey Stevens has been involved.

I went to one in San Francisco

and there were actually protesters outside,

which was kind of fun.

But they were like in very good spirits

and kind of like taking pictures with everyone.

It was a lot of fun.

Anyway, welcome to the stream.

Boom. How you doing? Hey man, how's it going? It's good. of fun. Anyway, welcome to the stream. Boom. How you doing?

Hey man, how's it going?

It's good.

What's going on?

Thanks for hopping on.

Chill week.

Your hair game is on point as usual.

Chill week for you.

You just been.

Sleepless nights.

Probably on maybe eight hours over three days.

Ooh.

Ouch.

Not good.

You should get an eight sleep.

Go to eightsleep.com slash TBPN.

I have a helix

No, it's great to have you on

What what's running through your brain? There's a bunch of things we could talk about but we're just aren't oh just the

Contagion effects and potential collapse of the world economy simple stuff, simple stuff like that, you know, how bad is it?

U.S. primacy.

Are you a, uh,

is there any element of cautiously optimistic about this for you or are you just

totally blackpilled on it?

Um, I mean, my white pills are Lucy's, so I do,

I do have some of those, uh, but you know, you're gonna need a higher milligram

for this week.

Well, walk me through why is it so disruptive to you

and what you do and maybe just for the viewers,

give a little background on yourself and the organization.

Sure, so I'm chief economist for the Foundation

for American Innovation, rip in the swag here.

FAI.

There we go.

We are a tech policy think tank in Washington, DC.

Originally founded to bridge Silicon Valley and the DC culture.

Today we work on the intersection of national security tech and governance.

I focus on AI, but cover sort of all economic issues as well. And, you know, I think we kind of,

or at least associated with the sort of tech, right?

With you guys like yourselves,

like I'm rooting for y'all and hopefully

Martin Scurly's Bloomberg terminal killer takes off

so then we can combine you guys

and completely disrupt Bloomberg.

So, you know, I think you see this in the administration too.

The Trump administration is a series of factions or coalitions and we are definitely in the

mix.

But you know, Elon Musk today called Peter Navarro, Peter Rotardo, and I kind of, you

know, definitely hard to argue with.

Can you talk about the bridge between Silicon Valley and DC?

It feels like that bridge is massive at this point.

There was a moment where maybe

tech was drifting away from DC,

but now it feels like tech has taken over DC.

At the same time, you go back to the Obama administration, I always think about this

statistic that I believe the number one organization that was non-governmental that Obama visited

during his eight years in office was Google.

And so there was a moment when Big Tech and DC were tightly intertwined, just happened

to be with the Democratic Party.

Now it happens to be with a Republican Party. But what is the state of the bridge and

how did we get here? Yeah, I think it's almost like a qualitative difference. So

if you think like the last 80 years the power structure in the US is being sort

of either Wall Street or like West Texas oil. So we either get like Rex Tillerson

or Jamie Dimon. Sure. And you know, since the internet took off, you know,

there's this new new wealth on the West Coast. And as that

sort of germinated and matured, it originally was just sort of

like one interest group among many, you know, they still still

had those two main power elites. And I think with the with this

last election, it was it was sort of an example of Silicon

Valley was a part of Silicon Valley, asserting itself as its own distinct power center.

Sure.

And that is very, very different. Of course, all the other power centers still exist to some

degrees, and so it is sort of a constant struggle. I think there's a lot that this

administration is doing great, the stuff on energy. I think Doge at some point is going

to turn to regulation, and that's what I'm most excited about. You know, once we start cutting whole

parts of the CFR, you know, back in the day, I used to do like supersonic policy and early

worked early with boom aerospace and it's good that they're getting a hearing now and

maybe maybe I'll be able to fly either coast and flowers rather than.

I'd love that.

So there's a lot a lot to like.

It's just, and I think there's also like a steel man case

for like these trade actions.

You know, we participate with like

the re-industrialized conference.

We have our own techno industrial playbook

that will be coming out in a couple of weeks.

So we're all on board for like, you know,

America needs to build again.

And you know, that, that especially

as AI like deflates all the knowledge sectors, like we're going to need more aluminum smelting

in this. Is there any glimmer of hope that there's this Marlago summit? I forget exactly

what Tramoth is referring to, but the Accords and you do see reciprocal tariffs, but they actually

have the effect of driving it down to zero tariffs anywhere in the world, either direction.

Are you hopeful for that?

Would that be a good outcome in your economic framework?

That would be sort of the best possible world.

There's also risks associated with that, right? Because I wrote a piece recently discussing

the sort of way the market reacted.

And on the one hand, you could say,

oh, Trump just likes tariffs.

And that's definitely true.

He's a 40-year track record of just liking tariffs.

But then you have other people like Steve Moran

and Scott Bessent and sort of JD Vans himself as well,

who at various points talked about the curse

of the US dollar being international reserve currency.

And there's a lot of truth to that.

Like the fact that China wants to hold our treasury debt

and they build cheap cars, we build treasury bills,

it does raise our living standards, you know, they build cheap cars, we build treasury bills,

is, you know, it does raise our living standards, but means that we are not ready to fight a war.

And so that is a core problem,

but then the question is like, how do you deal with that?

And if you do go all the way to a Mar-a-Lago accord,

what you're saying is, this isn't just about tariffs,

this is about resetting global financial imbalances.

And we need to do that,

but you need to do that sort of gradually.

Because if you do this all at once,

what that means is the entire floor will fall out

of the stock market and the real estate market.

And with huge cascading effects through emerging calls.

And I think mortgage debt is now back to its 2007 levels.

So it's less to me about like the mood or the ideas behind the policy, but the execution.

But this is a rug pull.

A rug pull.

Can you talk about the value of the yuan has been dropping?

I guess it's at a record low. Can you talk about trade wars turning into currency wars

and if that's what people should really be focused on?

Yeah, so China was a currency manipulator

throughout a lot of the 2000s and early 2010s,

but that really hasn't been the main way that they cheat.

They cheat by basically suppressing household consumption

and having these 60% savings rates.

And so they end up building these ghost cities

and whatever technology they enter,

whether it's cars or telecom equipment or pick your poison,

they just overproduce it to the maximum,

drive down the cost worldwide,

and then have to find these export markets to dump it.

And the way that we're ever going to resolve this is, especially now that the US is going to have 100% plus tariffs on China and Europe doesn't want their shit either, they need to build up

their domestic economy. They need to reduce their own savings rate, raise the standard of living of

their households, introduce some basic social welfare programs or something so that they actually have a domestic

consumer base. And if they do that, that's actually the best way that they can retaliate,

in a sense, because they're shielding themselves from the terrorists. But it also helps correct

the big imbalance. And so that is sort of aligned in sort of aligned in that sense where like, if China does the right thing, then it's a

win-win situation. If instead they double down on tariffs and

trade war. You know, I don't see I don't see that we just

exacerbate the the the contradictions in the economy and

don't get to a resolution.

Ben Thompson has been advocating for a rethinking

of the CHIPS Act, mainly shifting from export controls,

removing those and instead taking a more

operation warp speed approach where the US government

is potentially a massive buyer of domestic made

three nanometer, five nanometer chips with the

demand signal there, the American market should solve it.

How are you processing the current chips act and what are you hopeful for going

forward?

I'm not opposed to the idea. The thing about like, you know,

Nvidia's chips is they're kind of the demand is kind of saturated, right?

They can kind of pick who their buyers are because there's just so much demand for them.

And at the same time, they've not been the most sort of like loyal actor in this space.

And you know, if there's any sort of big meta narrative or theme to a lot of the tech rights

move into DC, it's been, you know, since from Project Navinon, that, you know, these companies have had

corporate social responsibility policies,

but not corporate patriotic responsibility policies,

and technology is becoming geopolitical,

and you sort of have to pick your side.

And so, you know, every time we introduce

an export control, NVIDIA's, two weeks later,

has a new chip that just gets under the line

of what's being controlled.

And the latest one is the H20.

The H20 is an inference ship.

It will power these reasoning models.

If we're worried at all about search being competitive,

I don't think we can give up on those.

And in fact, we should be doubling down.

And that would be like a smarter kind of trade war

than just across the board tariffs.

But that doesn't have to be mutually exclusive

with doing a kind of industrial push.

And that's what I'd like to see.

Because if we're going to do this big rebalancing,

you can't just pull the rug.

You have to, you know, to mix my metaphors,

you have to be the Indiana Jones

that like swoops in the bag of sand or something

as you take the Holy Grail.

And what is that, what is that like new thing

that we're going to be swooping in?

What is the industrial bank that we're going to be using

to bootstrap the industries that we need?

Because they won't just materialize on their own.

Can you talk about putting the trade wars

in the context of this race for super intelligence, right?

In many ways, people are arguing,

hey, if we're making Transformers harder to get

and more expensive, does that hold us back

from winning the AI race, and is that the only race

that really matters?

We've joked on the show about this idea

of picking up pennies in front of a steamroller, right?

AI has potential to transform the economy in so many ways

and it's very possible that just winning AI matters more

than winning the trade war in the year 2025.

No, I 100% agree with that take. Like, I can forgive a lot of stupid policy,

because in four years, we're going to have such powerful AI systems that like,

really it swamps everything else. And the you know, we know what the bottlenecks are going to be.

Right? Like the building these models only has a few basic ingredients.

You have the data and algorithms,

which the algorithms are basically public domain.

The data, China maybe even has an advantage

because they don't have privacy laws

and they can just scoop up everyone's genome or whatever.

And then it comes to energy and chips.

The export controls exist because right now

our only structural advantage is the chip and hardware stack

where our install base of Nvidia data centers

is a huge portion of the world's.

China's been basically cut off since 2022 and 23.

Then when it comes to energy,

China added 446 gigawatts of energy last year.

It was a 20% year over year increase.

They're going to do that again this year.

We added zero net new energy.

We added a lot of renewables, but it came directly out of coal and other sources.

The chips is the short one bottleneck, so that's why we need to lean into that.

And then the long run is how are we going to supply the energy? And then as the stuff diffuses, you know, to the

people who worry about deindustrialization, it's like, it's true. The last 40 years, we've

specialized in, you know, higher education, knowledge work, legal management services,

Hollywood, you know, the creative class, all the stuff that is going to like be deflated.

And China will have the factories

that will become fully automated and due course,

because they'll also have the workforce

that they can extract all the tacit knowledge out of

and put into their robots.

And so it's a really urgent thing

that we don't just try to win on AI,

but win on AI plus heavy industry and robotics,

because otherwise our innovation in bits

will be their innovation and atoms.

Yeah, the one point of view on the trade war

and trying to bring manufacturing back to America

is like, yeah, we can bring the production capacity back,

but will the jobs come back in the same way, right?

Just due to, if we actually want to scale production,

we need to lean into automation and robotics.

How do you think about job creation as part of reshoring and increasing domestic production in the context of long term, a lot of production just becoming automated and just just because that's going to be the most efficient way to produce

the most amount of goods.

Yeah, we need to bring back manufacturing, but it's not a jobs program.

That's for sure.

In fact, the only way we're going to bring it back is if we automate significant amounts

of this.

And maybe the guy who presses the on button every morning gets paid multiple six figures,

but it's not going to be this nostalgic vision of like the 1950s

where we're all going into the factory. And that's just like a structural thing. AI is

going to do that for a lot of stuff, probably most stuff at some point, and we're going

to have to figure out what the new jobs are. I saw a video of professional backscratcher.

And you know, I saw a video of like professional back scratcher. Yeah

I know in the VC world those exist already but like

But this was like a woman of long acrylic nails and some you know, maybe we can start growing our nails at

Crazy cases that there's like there's there's so much knowledge work to do around an advanced factory I mean, we just talked to Jay from the advanced manufacturing company of America. There's clearly a lot of high skill labor that is not getting displaced anytime soon

that could...

That's not millions of people.

Yeah.

Well, it might be if we're manufacturing a Dyson sphere with a million robots or something.

I don't know. I could see a world where, yes, there are a million jobs in the manufacturing

sector, but it's all at the higher level.

But if 2 million traditional white collar jobs

get evaporated.

In the interim, maybe.

There's clearly some big questions

we're going to have to be thinking about.

Do you have strong opinions on UniTree or any

of these other Chinese robotics companies that are trying to?

He's just like, I love them.

Yeah. I'm curious if you've written about it, if you've had,

you know, policy recommendations that you or F.A.I. have made around,

you know, some of these more hybrid sort of dual use.

Well, everything's dual use in China.

But what do you think about Unitree?

No, the Unitree is really impressive.

I've seen it do Kung Fu, and it does break dancing better

than that Australian lady.

Oh, yeah.

Yeah, and if you, Shenzen is like going to a flea market

wherever you trip over baskets full of microelectronics,

and we need to be building some of those ecosystems in the US.

That's number one.

And number two is like, yes, we have the data centers and the better models, but China has

the batteries, right?

They have like, that's one area where they have leapfrogged us.

And whether it's electric vehicles or robotics or drones, like we need to have our own battery stack

and maybe, you know, we do need like a chip sack too

but we also probably need like a batteries act

to compete with that because that will be the thing.

It's fine if, you know, Andrew will build a drone factory

but where are these batteries gonna be coming from?

Yeah.

Not asking for financial advice, but where specifically

in America are you long?

Areas that could be that sort of American Shenzhen,

or maybe it's multiple places.

I'm curious what areas that different regions in the United

States are, do you think, benefit from reshoring

most intensely?

states are do you think benefit from reshoring most intensely? In recent history it's been sort of the south and South Atlantic, you know, the North Carolinas,

the Tennessee's, Nashville, you know, partly because those are all the best housing markets,

right?

It's so much easier to build when you have Greenfield.

But longer term, this is also not something that the US can do alone.

We're going to need almost like a North American

plus production frontier where,

let's figure out the thing with Canada,

do we need their lumber, don't we?

Do we want their bags of milk or not?

But like we do need their aluminum, right?

And we will need to have some kind of integrated

production ecosystem to be kind of competitive

and stand up to China.

Cause China, you know, already in purchasing power parity

is larger than the US.

And you know, they to gobble up their neighbors

too and get even bigger so but I do think there is an opportunity here

because when you do have like I'm not a technological unemployment guy you know

I think new jobs get created they'll just be very weird not necessarily in

the sectors that matter the most like the purpose of industry heavy industry

and robotics is like more military and like do we control the purpose of industry heavy industry and robotics is like more military and like

Do we control the supply of core goods and services?

On energy, what do you think the lowest hanging fruit is in terms of energy deregulation?

Should we be focusing on the NRC nuclear? What's the biggest?

Opportunity to help us jump from I guess 0% to 20% where I wanna be,

maybe 40% would be nice, maybe 200%.

Yeah, you guys should definitely have my colleague,

Thomas Hockman, on to talk about this for a full half hour

because he's been putting up the winds lately.

We've helped pass a bill in Utah.

There's activity in Arizona, Montana, other places.

There's a huge appetite to unlock America's energy.

In the short run, especially for these data centers,

it's going to be natural gas.

It's going to be a bridge to more permanent

base load energy.

And then the next bottleneck is the grid itself

because if you want to do a,

even if it's just like natural gas generators

are rolling in, like that investment makes way more sense

if you know that after that, you know,

GPT-7 is trained that you get to put your energy back

into a grid and have customers for it.

So that needs to be fixed.

Other energy sources, you know,

I think enhanced and advanced geothermal, they were underrated.

I think people are starting to finally wake up

to the potential.

Really advanced geothermal, we could make everywhere

in America kind of like Iceland,

where you have energy under your feet.

And then with nuclear, there is this case before the courts

that I think is Texas, Utah versus the US

government that NRC that argues that the NRC doesn't have jurisdiction over small modular

reactors.

And I think there's a good chance that this, that Pam Bondi and the attorney general settle

that case, in which case states could then stand up their own licensing boards.

And I think there's actually already

Movement in Utah to have their own like nuclear regulator and so that could that could happen sooner than people realize

Do a bunch of young founders building, you know small nuclear reactors. Is that scare you? Does that keep you up at night? Or do you think the technology is you know, it's solved

Radiant isn't that young? He's got kids

I trust him with my life. Yeah, basically I think it's a requirement

You should you should have to have kids to be a nuclear. He worked at SpaceX. He's got the pedigree

I love that company based in El Segundo

the big problem of nuclear is it it's it doesn't really pencil out without like large government support, yeah, and

It doesn't really pencil out without large government support. Yeah.

And so I would love to see the $600 billion in tariff revenue

be given to Doug Burgum to build a reactor template

and build 200 of them all around the country

and use every national security, national emergency trick

in the book to get it done as quickly as possible.

But it will need some kind of fixed capital backstop

to make those investments,

at least with the current technology.

I mean, given what you're kind of optimistic about Doge,

it seems like you're pretty bearish about the tariffs.

Are we in a regime where you trust the government

to do mega projects yet?

Because I think everyone was excited about

the moon landing. And then since then, a little bit less excitement about the big projects,

high speed rail in California has been a little bit of a rough go. And I don't really want

to see a California high speed rail of 600 billion get burned on a nuclear strategy that

doesn't produce a single watt of electricity for 70 years you know 70 years or something which would be like the bad case

Yeah, a hundred percent

You know the state capacity and competence is really you know, it's the jagged frontier

Yeah, there's places that have a lot of it places that a little of it

You know, I would have more you know, I would have more trust in a burgram or a Chris Wright

of actually executing on something like that.

It wouldn't be the Pete Buttigieg slush fund

where it's just filling potholes in Indiana.

They would know how to cut through the road tape.

They wouldn't make it like this, everything bagel,

we're going to build TSMC chips,

but then also rehabilitate justice involved individuals.

You know, we need to keep our potatoes and our gravy separate.

Got it. How are you thinking about the deep sea versus metas llama strategy?

We were talking about that earlier on the show and it's kind of hard to,

to, I think a lot of people on the vibes of

DeepSeek, they're like, I don't like this.

But then it's difficult to formulate an argument because are you anti open source?

In which case are you anti-Zuck and meta?

How are you thinking about kind of the intellectual property that's being developed in America

around large language models and then makes its way across the Pacific Ocean.

I think what I find most impressive about DeepSeek

is less that the model they put up,

but just that they sort of have imported

a kind of Silicon Valley model of like,

and that came from their CEO being like a hedge fund manager

of doing this as a side project.

It's very, you know, Sam Altman wasn't a hedge fund manager,

he was a VC, but sort of analogous, right?

And that's striking because

it's just a different model of corporate governance

than you're used to seeing.

And I think there's a question of like,

how long, does Deep Sea become a victim of its own success?

And like, you know, they are the tall poppy.

And it's not that China tries to hurt them because of that,

but actually tries to help them

and makes them a national champion

and thereby sort of perverts it.

And, you know.

It's a fun take.

They've been great to, you know,

publishing what they're doing

and everything sort of has checked out.

But they don't have the chips and they've said that.

Like their CEO said their biggest bottleneck is hardware.

And so we shouldn't help them on that front.

Like there's $16 billion of orders for H20s

just sitting in limbo about to go at the door.

The Commerce Department has,

Howard Lutnick has said that he's going to

export control at age 20,

but they're so distracted by tariffs,

they haven't prioritized it,

and the time is kind of running out.

What's going on with TikTok?

We've been following the poly market

around a new band before May.

There's markets around,

potential buyers, things like that. Do you have any insight that you can share

around the latest there?

It feels like, again, one of those things,

it's just like not getting the attention and the focus,

because obviously, if we enter into the greatest

global trade war of all time,

yeah, it's rightfully people should maybe be

sort of focused on that.

But at the same time,

it feels like something that we were supposed to have

answers around by now and we definitely don't.

Yeah, totally.

I mean, FAI, we, we led the charge to,

to ban TikTok over a couple of years.

And I fully support it.

I also enjoy TikTok,

but I do notice that like

between my barbecuing steak videos and like funny memes,

I'll get like a Pyongyang tourism board video now and then.

It's like, well, I don't plan on

visiting North Korea anytime soon.

But yeah, I don't have any super deep intel. You know, there has been talks about

or rumors about, you know, Oracle maybe being part of this. And I think Trump still wants it to be

part of the new sovereign wealth fund. And actually, as sort of Zanian idea that is, like,

he kind of has a point, like if TikTok became American, and, you know, quadrupled in value, that would actually help

pay down the debt.

The interesting thing here is like, you know, people have pointed out that, you know, Trump

is sort of placed fast and loose with the constitution, with the law and stuff like

that, you know.

And matter of fact, all the people he's fired, totally constitutional.

The biggest, the most unconstitutional thing he's done today is not enforce the

TikTok ban. Oh yeah.

Cause that was a direct, you know, statute that Congress passed that said,

thou shalt ban TikTok. So I,

I I'm hopeful that they can get a deal that the reason I would just doubt it is,

is China has very strong expert controls.

Like the reason to talk can't sell is because algorithms

in general are expert controlled.

And so they would be able to buy the brand name

and like the offices,

but they have to completely revamp the algorithm,

which is like the secret sauce of the thing.

Now TikTok is in our building in DC,

so I can try to plant a bug for you if you want.

Sounds great.

Well, that'd be fantastic.

Polymarket has the chance of TikTok

being on the app store on May 1st at 97%.

And who will acquire TikTok?

Oracles at 27%.

Number two, Larry Ellison directly at 24%.

You'll love to see it.

Amazon's still up there.

But I just want to say thanks so much for joining.

This was a really interesting conversation.

We'll have to have you back soon.

Yeah, and get some sleep.

Yeah, get some sleep.

We'll work on getting you an eight sleep

so you can start putting in some proper sleep.

I want to see 100 for a week straight.

I think.

Yeah, less red light from the stock market.

More.

Yeah.

Yeah, more sleep.

Anyway, go get some sleep.

Thank you for coming on.

And yeah, look forward to the next one.

Yeah, talk soon, bye.

Later, man.

Cheers.

Next up we have Shiel coming back on

for his second TBPN appearance.

We're gonna talk about FinTech, the markets, the tariffs,

his dust-up with another capital allocator on Axe the other

day, had a lot of fun with that,

and I'm sure we'll have plenty to talk about.

So as soon as she'll gets here

We'll bring him into the studio

But those are some interesting questions. There really are so many

Debates right now. It's like DJI unitree tic-tac deep-sea. There's like seven different

Really important questions. Maybe we'll talk about it with shield

Maybe we won't but let's bring him in to the studio

and welcome him to the show.

Welcome.

Boom, back with a suit.

Looking great, how you doing?

Looking good, looking good.

Guys, no Apple Watch.

No Apple Watch, there we go.

There you go.

We'll get you on Bezel now, that's the next step.

We've de-radicalized you from the Apple Watch,

next is radicalizing you to Bezel.

Yeah, the tariffs haven't hit the secondary market yet

No, it's a great buying opportunity. This is financial advice go to get bezel comm download the app just for shield

Just for you not for you specifically you specifically I want to see an item our pig a or

Royal oak on you something like that

well Adam R. Piguet or Royal Oak on you, something like that. All right, all right. Well, you've had a bit, I feel like you've been,

the timeline's been in turmoil

and you've been at the center of it.

Timeline's been in turmoil.

In turmoil, yeah.

I guess Chamath knows who you are now.

Yeah.

Now that people reminded him

that he would use your content in his newsletter.

Yeah.

But. That's so funny.

The whole thing.

The whole thing was funny, I'm sorry

I mean, I honestly probably good metrics. I'm sure we're up into the right. So you know, I'm boxers the creator payout this

It's gonna go from 200 bucks to

Screenshots of his content with just this is why I can't believe this app is free

and this is why I'm never deleting this.

I'm never leaving this app because of the interaction.

Yeah, exactly.

Anyway, can you give us just your high level reaction

and how you've been processing the tariff news,

kind of set the table for us and then we'll dig in.

Yeah, wow, right into it.

Okay, I'm kind of like,

I've always been more of a free market kind of guy.

An American. And I think,

free market American, yeah, American.

I've been an American guy.

And I tend to think competition makes us better.

And I also like spent time

like living in protectionist India.

And so for those who don't know,

like until the 90s, India was a closed economy.

They had super high tariffs on all foreign goods and it sucked.

There were two local car manufacturers and the cars were built in the 50s and they didn't

get any better from the 50s until the 90s because India had so much protections on their

local car industry.

And that was terrible.

So like they didn't innovate,

they never improved the quality.

They were super high so people couldn't afford,

the prices were super high so people couldn't afford them.

And so that's what really scares me.

And then you might say that would never happen in America,

but you'd be totally wrong

because that's exactly what has happened in the US shipbuilding

industry.

So, like, the Jones Act basically says that if you're shipping goods between two US ports,

you need to use a US-built ship crewed by US citizens and owned by US citizens.

So like, it's super protectionist in the US shipbuilding industry and US ships

suck. They're like five times as expensive as other ships and they've never had to innovate

because they have these protections. And then it totally distorts the markets in general.

Like on the East Coast, I'm in New York right now on the East Coast, a lot of like the East

Coast gets some fuel from internationally because it's easier to ship here

than it is to get it from Texas.

And that's just like a perversion of markets

that exist because of the Jones Act.

So anyway, so I think like all these things,

like I'm totally anti-protectionist.

There's a question of like, what is Trump doing?

Is like with, it's not really a reciprocal tariff.

Now everybody realizes it was a funny situation last Wednesday when people were like, what

the fuck are these numbers?

And then, you know, the guy who did the math was like, oh, this is about our trade deficit,

not reciprocal tariffs.

I think like, if you if like, now people are coming around around and saying oh, this is all about lowering trade barriers

I think that's bullshit because like you have Lutnick saying like we need millions of Americans screwing in tiny iPhones or whatever

And and you and they also say that the tariffs are gonna replace income taxes

So if those things are true, then it's not about leveling the playing field to zero.

It's about like putting these tariffs in place to reshore.

And I personally don't like that.

Isn't it fascinating too?

There's this focus on trade deficits, but we're completely ignoring like services and

specifically like digital services.

Right.

So it's like like Switzerland for example.

You know we have a trade deficit because they have eight ish million people and we have

hundreds of millions. And then they like make all the world's fine watches which we just

talked about. But then like they also probably love Netflix.

Yeah I guess I guess that like a lot of people in Switzerland are subscribed to Netflix and

we're just like completely ignoring all of that. Yeah, and and you know, yeah

Just most prosperous country in the history of the world. Yeah, fucking awesome

You can afford to buy all their shit like I don't need to buy stuff from us. They can't afford it

So it's not it. Yeah, so the steel man here is like

First off do you think DJI and the consumer drone market

is a problem?

And then if so, what is your solution

if not just ban DJI, tariff DJI?

We did a deep dive on GoPro versus DJI,

and it really just felt like China was like,

we are going to kill GoPro in the drone market,

and they put so much firepower behind it.

And I'm like, I still get that there's some weirdness going on here.

And it's important industry and there's dual use.

And there's a million different factors.

So how do you walk through that specific example narrowly?

Let's let's let's take away the blanket.

I walk through that for me.

And how would you solve this in a more free market, more progressive fashion?

Yes, that's a great question.

So the first like we have tariffs in every country, not just our enemies with Trump.

But China specifically, I do think China is playing unfairly and there are enemy and we

shouldn't let our enemy get data on the United States.

Like that could be really bad.

They're definitely our national security issues with drones.

I also think we should ban TikTok.

And so I think those things can be dealt with, but they have nothing to do with terrorists.

Yeah.

I guess one of my scenarios would have been if I could replay everything with everything

I know now, maybe you see what's happening with DJI and, and GoPro and you say, Hey,

we are the richest country in the world. Uh, we do have,

China buys a bunch of our debt.

Let's lever up essentially and create a drone buying program from the government

to stimulate demand for American made drones.

Essentially backstop GoPro,

let them get down the learning curve.

Hey, if they make these drones in America,

we're gonna buy them even more.

And let us develop that and then we are competitive

and we say, hey, it is a little bit,

we're still shifting the invisible hand,

putting our hand on top of the invisible hand,

but it's still somewhat of a free market

in the sense that like,

just like what we did with EVs with Elon,

like anyone could have gone for those electric vehicle incentives.

Elon did a great job taking advantage of it. Like, and we got a great product.

It sold really well eventually.

Yeah, I think that's absolutely right. I think, and like, look,

we moved in this direction already. Like the chips act and IRA both,

did make good moves like they they enable they

subsidize US chip manufacturing that are critical for military

systems and other stuff. I think they have made some moves away

from foreign chips. And so that also that all stuff is good. I

think like meeting with a carrot is way better than leading with

a stick personally. And I think like the the ideas

you you mentioned John are spot on. And by the way, like we

helped Tesla along the way, like we loaned the US taxpayers loan

$500 million to Tesla. Yeah, like that kind of thing. I'm

totally in support of totally enable us manufacturing to be

better to compete on an even playing field by being more innovative,

not by blocking other countries from competing.

Yeah, yeah.

Jordy?

Bummer to see the IPO window close.

We had Klarna, StubHub, we'll see if Circle gets out.

Klarna would have been especially nice

for FinTech broadly to get some marks.

Circle still at 86% on Polymarket for this year.

Yeah, they might just be like, you know, crypto, we were born in the darkness.

We're going out.

We're going out.

Did you have a take on the Circle IPO in general?

I saw a lot of people just were not kind of loving the S1, particularly just based on how much they were paying

Coinbase to distribute the token.

I'm curious if you had a take on the IPO

or dug into it at all.

And you don't need to have any knowledge to have it.

You don't need to have any knowledge to have a take,

by the way.

That part of.

Yeah, no, I would say like on Circle in particular, like I saw all the same stuff you saw.

Coinbase gets half of the revenue from Circle's token and all this other stuff.

But I don't I don't have a strong take on how the IPO will perform.

I tend to think that these things are somewhat like initially somewhat disconnected from

the reality of what's going on.

So like I think, you know, we talked about bridge last time I was on and I think there

became this stable coin hype.

And I bet if Circle was public at that point, they would have gotten a huge bump for no

particular reason.

Totally.

Yeah.

But I think overall stock market.

Yeah.

Like what does what does Polymarket say about Klarna?

Is there a market for that?

Oh, I don't know.

Jordy, can you get up?

Well, Klarna, I think officially pulled their...

It pulled.

Well, like the thing is these tariffs are especially, especially bad for Klarna, right?

Like it's consumer discretionary spend that you use BNPL on and consumer discretionary spend

in a recession or with high tariffs,

like goes to the toilet.

So like you're not buying that extra $2,000 item

that you didn't exactly need.

And that's what you were BNPLing anyway.

So I think we've seen a firm stock.

I think our firm stock got cut in half.

Yeah, I want to go deeper on Circle because I feel like it's one of those companies

that if they're about to IPO, I can't even name the founders.

I don't know all the big investors. Like it's this, it's this fascinating.

This is a case with a lot of, uh, a lot of crypto companies,

but even bridge, like we heard the story of like who made the money on this.

Okay. They got acquired by Stripe.

Like they're very much in the Silicon Valley world and circle obviously is but has been, hasn't really told their story

in the way and so it's interesting, they could have a meme stock moment where

it's like the, it's the primary way that you get exposure as a public markets

investor to stable coins broadly, I guess, and that could be a good narrative, it

could just be a meme stock because, hey, crypto, it's, you know, whatever. But they haven't really told their story in a way that's broken through, at least

with me. I don't know if you've processed it any differently.

Yeah, I think it's certainly less hyped than a lot of the others. The CEO, Jeremy Allaire,

I went to a stablecoin conference a couple of ago and he spoke and so he's very sharp.

And he's been at it for a very long time.

He's like of a different,

slightly different generation than us.

Like he started a company that IPO'd in like the 90s,

like Donkomboom.

And then he was actually a venture capitalist.

Like he worked at General Catalyst for a little while.

Oh cool.

And then launched Circle, whatever, 10 or 15 years.

Not obviously not 15 years ago.

Yeah, but I didn't exist.

But but yeah, that was the best time to launch a stable coin before Bitcoin really early.

I mean, here's the bull case for USTC and like and here's my bull case.

Sure.

So Tether is like the most profitable financial institution

ever, right?

It's literally, what are they?

Is it $8 million?

It's like $50 million per employee or something in profit.

I forget the actual.

You probably shared it at some point, Shield,

but it's like some absurd number.

They're more profitable than any of these other major financial

institutions.

The risk with Tether is like it's opaque.

You don't fully know what's going on.

Like there could be people for a long time said there could be

systemic risk associated with Tether.

They've been accused of a lot of stuff over the years.

I'm silly.

Yeah. Yeah. But they're dominant from a market cap standpoint.

The second the second biggest stable coin is

is USDC

at a $60 billion market cap,

and a market cap is obviously just one to one

with the supply, right?

And then you go down the list, the next one is DAI,

which is also run in this very crypto native way

from what I know.

And then you are, to get to the next stablecoin

made from a sort of true traditional Western

institution, you have to go to first digital USD, which is under a $2 billion market cap.

And below that is PayPal USD, which is an $800 million market cap.

And so to me, I'm looking at Circle and it's like here's like the power law winner the dominant, you know They're 80 they have 80 times the circulating supply as their next like regulated, you know Western institution and

They have USDC. It's a pretty good

Not super sophisticated but it you know brand matter

I mean we talked to Zach parade plaid and and we were like, if you had full authority,

you were like the president,

could you speed up wire transfers in ACH?

And he was like, absolutely, but it's not gonna happen.

And so it's like, yeah, maybe stable coins are here to stay

and all the pitch about just, hey,

you're just gonna be able to transfer money two days faster.

Like, that's enough, even though it seems like

you should just be able to speed up the government transfers.

What's your read on any sort of predictions

on venture right now?

I think that the lesson in venture since 2020

has just been take advantage of chaos,

invest through market cycles, never stop deploying.

I remember in 2022, we were talking about the,

what is it, denominator effect. Denominator effect, yeah. I remember in 2022, we were talking about the,

what is it, denominator effect.

Yeah.

Denominator effect, yeah.

Denominator effect, but then it didn't fully play out.

We saw this, I mean, we saw like a, again,

a bifurcation of like the big funds,

raising all the money on paper.

But you know, if you're a specialist fund

with like a strong story, you can, you know,

still get funds done.

But I'm curious first about the venture market, then I want to kind of ask more about portfolio

stuff.

Yeah, first, maybe a fun tidbit for you guys is just the last few days, obviously, markets

have been in various states of turmoil.

And venture capitalists, some of them are like trying to seize

the day where like for example there have been a couple of companies in our portfolio

that some investors have been really trying to invest in but the companies are well capitalized

and don't need the capital and now the investors are like hey markets and turmoil might this

be a time that you would consider taking my money.

Yeah.

Yeah. Yeah. You don't have to be living up to the vulture capitalist name. I like it.

Yeah. How do you how do you even think about there's going to be some

enterprising founders that are like, look, I'm building a startup around

that's that's, you know, built to help solve global supply chains or something.

Yeah.

Like the chaos is a ladder.

I'm going to take advantage of this.

To me, it's like, OK, if we're entering this sort of protectionist phase

of de-globalization, maybe it's too early to make bets.

But yeah, how do you see companies actually being able to make something

out of the chaos

or are you just telling your portfolio,

just stay focused on the customer,

ignore the noise, that kind of thing?

I truly like stay focused on the customer, ignore the noise.

I think we don't have any companies

that are like super exposed for some reason or any other.

I saw you guys have Jay Malik coming on later today,

which sounds like he timed that perfectly.

Yeah, it is crazy. Yeah. Like literally.

I mean, there's a few of those companies that are been,

I mean that's been the thesis for a while, just general reindustrialization,

but they really hit a royal flush this week.

Yeah. So, you know, it's mostly stay the course.

I think like people are saying, OK, venture capital dollars are going to decline.

But as you know, like the way it works is we raise a fund every few years.

Yeah. And we have plenty of capital.

So like it's not like, you know, an LP, there's some impact on the markets today, and that means we don't have

money tomorrow.

It's like, if there is any impact, it's a few years out.

Though it doesn't change how we invest.

Now the later stage investor is it is a different equation because for them, they have a certain

timeline they're hoping these companies go public.

And if the public markets are kind of frozen, that makes things difficult.

And like they're thinking on an IRR basis, like has their opportunities have declined

if they can't, if the companies don't get out at a reasonable time.

Yeah. So mostly just texting founders in the portfolio. Have you seen this with a screenshot

of the market? That's just what I always do. Yeah, exactly. I want to get your reaction

to this post from Semmel over at Haystack. He says seed is again going to

be the hot zone where nearly every VC fund will want to invest. Just like when COVID

struck and in the early in early 2022, VC shifted early to balance large checks by firing $3

million seed bullets. LPs should expect median

seed entry prices to be up 50% in the next vintage. Does that seem like a good

take or what do you think? No, I like I love Semel. Yeah. But I don't know if I

buy that. Seed prices are pretty high right? That's the thing. Please, please, please.

Don't tell the founders. It's like wait a, right? That's the thing. Please, please. Please, please make it lower.

Don't tell the founders this.

Don't tell the founders this.

It's like, wait a minute, I can raise my safe by 50%

with one stroke of a pen?

Let's do it.

Yeah, it doesn't make sense to me because,

so we started this fund in 2019,

and actually the seed valuation is,

2021 was an insane time, especially in FinTech,

like everything we were investing in seemed like it was

like turning to gold and then, you know,

and then maybe turning to shit afterwards.

But, but, but, but, but that,

but actually like seed valuations have actually increased

from that time.

And it's basically kind of been as like a straight line

upwards and what he's talking about actually started

happening in 2022.

And a lot of the funds invested at Seed in companies, you know, and the problem is,

if you're a multi-billion dollar fund and you write a two million dollar check

into a company and you invest in the wrong company in the category,

like you don't get a chance to write a 250 million dollar check into the right company.

So I think it's pretty foolish when those funds invest at seed.

And we have a bunch of examples now of like, of friends of ours who took money from a multi-stage,

but like the multi-stage doesn't care about them that much because it's a small amount

of money. So I don't know.

I'm skeptical that this is going to happen again or that it's going to really

accelerate and prices are going to go up. I don't know. We'll see.

Well, we should make a bed and have Peter Walker from Carta give us the data in a

year. I love his stuff.

Can you talk about, there's this meme of like, oh,

for a while if you're building a consumer

or something, like you're gonna get steamrolled by what if Google builds it, right?

And there's this story that Google is allegedly paying some AI staff to do nothing for a year

rather than join rivals.

Hilarious.

I want your reaction to that.

But then I also want to know, like, is there, does that meme exist in FinTech?

Is there an idea that, oh, AMX or Visa or JP Morgan

are gonna build this?

And has that ever actually happened in practice?

Well, yeah, and even potentially on that,

I'm curious, like, open AI wants to run your entire life.

Yeah.

Have you heard any sort of, like, rumors

or is any concern around people saying,

oh, I'm building a consumer agent, you know, for financial consumer financial services. But then opening I might be like,

oh, by the way, we launched a partnership with Chase and or we launched a partnership

with cash. Yeah, we can analyze your credit score now with an agent and that that model

that that rapper company got steamrolled. Yeah. What's your take on all that?

Okay. So first thing I think you said was the rest invest situation.

Yeah. Where?

And so I thought it was really funny because you guys watch Silicon Valley, the

TV show. Oh, yeah.

So good.

And there's that obviously there's the phrase rest invest.

I learned it from that show.

And it's certainly playing out.

I had no idea that that that phrase was like popularized in some way by the show.

Oh, yeah. Yeah.

I thought it was I thought it was a 2021 like big tech thing.

No, no, no, no.

This is the thing going back a decade.

If you haven't seen it, you got to go back and watch it.

So I never could get into it because I it was just too close to reality.

Yeah, yeah, same thing.

Like the most, it was not like, I watch TV

because I wanna not think.

Yeah, totally.

Watching Silicon Valley, it's like,

oh, that's an email I need to reply to.

Exactly.

I should follow up with that founder.

My first company, Soylent, was in the intro

to Silicon Valley, in the intro sequence.

And they're just making fun of me every

single day. Also, one of the creators went to my high school and so like I knew him and he's like

actively poking fun at me every single episode. Amazing. That's amazing. It was great. But yeah,

it's very silly that Google would let this even leak out. I don't know how that happened.

Totally. It's crazy. I mean, the things you hear out of Google are so crazy.

I think more, more so than any other big co,

like my wife works at Metta and they've like really got their shit together,

like the year of efficiency, stuff like that. I think probably before then it was,

had stuff like this, but not now. Okay. So that was, that was topic one.

I think topic two was like, what if X company builds this?

And is that the case in?

Fintech. Yeah, I I don't think so like in fact you actually had look one one of the sponsors ramp though

Stripe had built right right had a corporate card and

It didn't work like they ended up investing in ramp and deprecating that card

so I think people have tried to do stuff.

There is the what if Stripe does this,

what if Plaid does this.

And there are, in some cases, I think that's totally valid,

but for the most part,

I think there's plenty of green space out there.

And, you know, Stripe has been acquisitive.

Obviously we talked about that before.

There's nothing I'm super afraid of.

I will say in some categories, like, for example,

in wealth management, there was the wealth

fronts and betterments of the world, the robo advisors,

and people said, OK, we're not charging 2%.

We're going to charge you 25 bips.

But the reality is that the service offered

by somebody who's charging 2% is different than what

they offer at 25 bips. And the 25 25 bib solution was fairly easy for Vanguard to build and Vanguard became by far the largest

Robo advisor in the world got it

But I'm not I'm not afraid of that in general

Infant you much. Do you think that up?

Do you think humanoid robots present an opportunity for loan sharking?

Do you think humanoid robots present an opportunity for loan sharking?

It's like hey we're gonna offer you this great rate whatever it's secured against your kneecaps

It's funny like we are tagline for our fund when we started it was everything is fintech

it would be funny if we invested in a humanoid robot company and then just we were like dead pan, like, what do you mean?

Like obviously the use cases for loan sharks.

Yeah.

Yeah.

Obviously.

I mean, I was talking to a sales guy.

I'm curious, like my thought goes with,

do you think that AI can get, is already or could get materially better at underwriting

than a human just spending months on an opportunity?

And is that something that, do you think that FinTech broadly has fatigue around investing

in AI lending just because it's been sort of this like ongoing narrative isn't there like what's the what's the public company that was sort of promising this

for a while something I mean there was Metro Mile which was better underwriting

upstart but even Metro Mile was better underwriting for your car insurance

based on how you drive they put a GPS tracker and like a gyroscope in there

basically see if you're stomping on the brakes every two seconds,

give you a higher insurance premium.

A lot of promise there, but not a lot of, you know,

massive adoption over time.

I think they didn't execute that well.

And I think with Metro Mile,

there's actually Root has done a better job of it,

but Metro Mile, it was primarily just mileage-based,

the number of miles you drive.

And then Root gives you a phone. You put your phone in it, but Metro Mile, it was primarily just mileage based, the number of miles you drive and then Root gives you a phone.

You put your phone in it, like checks if you're braking hard and where you're driving and

stuff like that.

So I think that there are opportunities to be used in insurance.

In underwriting for loans in particular, it can be tricky because the regulatory framework

in the United States, Equal Credit Opportunity Act, Worker Reporting Act, et cetera, you're the regulatory framework in the United States Equal Credit Opportunity Act, Worker

Reporting Act, etc. They you're not allowed to discriminate on

the basis of race and gender and some of these other things are

tied to that. So that that can become tricky. And you're

actually you have to respond, you have to give people the

reason why they were denied, like it's adverse action notice

So you can't have a black box model. That's like

Here's all the data. They just give you a massive matrix of weights and they're like this is why you're denied

Figure it out Totally

That tensor number 76 was activating for you. So get out of here

Yeah Number 76 was activating for you, so get out of here. Yeah.

So actually, if we didn't have that, lending would be probably more efficient and you'd

better be able to target the right customer, but we do have those things for a reason.

And so we can't have a black box model.

And so there are actually companies,

we invested in a company that's like,

in part detecting bias in AI underwriting for this purpose

to make sure that you're compliant.

Yep.

And yeah, so anyway, I think it can be used

and can be super useful,

but because of those regulatory bound guidelines,

I'm not sure it's gonna be a step change in underwriting.

Yeah, makes a lot of sense.

Jordy, last question, you wanna let Shiel get out of here?

No, this is great, always a pleasure.

Always fun.

Different fun, guys.

Looking forward to the next one.

Yeah, this is great.

Likewise.

Have a great rest of your day.

Godspeed.

You too. We'll talk to you soon.

Well, we got some breaking news,

another massive funding announcement coming in

to the studio, Victor from Craya, is that how you pronounce it?

Craya is coming in.

AI video company that just announced a massive fundraise.

Let me look up if I can find the details of this fundraise so I can get everyone up to

speed before we bring Victor in here the website is crea.ai kre a and they just announced a huge funding round 83

million dollars just a couple million over over J not that it's a competition

they got Andrews and Horowitz being capital in the round.

The past 14 months at Craya have been hectic.

We rolled out over 50 major product updates,

grew to over 20 million users organically,

and they 20x their revenue, all with a team of eight

working out of a living room in San Francisco.

That is fantastic.

You love to see growth like that.

Doesn't happen every day,

but it's happening more and more in AI.

So excited to bring Victor into the studio

and talk about that.

They write, the numbers are exciting,

but they can miss something crucial.

The team behind it all.

Craya is the work of a small, talented group

of imaginative, incredibly dedicated people.

And yes, most of us still live together.

That's fun. Until now, we've never shared metrics or announced our funding. Heck,

we didn't even have a blog until a few hours ago. Those details always felt secondary compared to

what truly matters to us, making AI intuitive and controllable for creatives. Now, after the release

of our redesign, the growth of our team and recent funding,

it feels like the perfect time to open up

about what inspires us and what we're building towards.

So they write, we're living through a moment

where everyone talks about automation, APIs,

and how AI and software are eating the world.

Perhaps too much, don't get us wrong.

While AI is powerful, transformative,

and is going to radically change creative work,

creatives aren't going anywhere.

40,000 years ago, we painted red ochre onto cave walls.

Later, we drew with graphite on paper.

Today, it's complicated.

We use cameras to digitize light through glass lenses

and silicon sensors, transferring data through metal wires

to illuminate the LEDs lighting up the screen

you're reading on now.

How do you know I didn't print this out?

I could have printed this.

The printer still works with TBPN.

We might have shifted to laptops,

but you never know, don't assume anything.

No, I am reading this on the screen.

And old tools and workflows.

Do we have Victor in the waiting room yet, by the way?

Not yet.

Old tools and workflows will disappear,

but our creative itch won't, and I agree with that.

Excited to dig into that with him.

We will build new and more powerful tools

to keep doing what we've always done,

master new mediums for self-expression and storytelling.

AI will render some tools obsolete,

but not the people behind them.

We see AI as a new medium that lets us express ourselves

through any format, text, video, sound, and even 3D.

Such a medium needs better, smarter,

and more controllable tools.

That's where Craya comes into play.

They say, it won't replace, AI will not replace creativity.

Creativity is not disappearing,

but the walls between creative mediums are.

Traditionally, excelling in one creative medium

rarely translated smoothly into another.

AI changes that, and we're bringing Victor into the studio to tell us more about Crea

and the fundraising.

So welcome to the stream, Victor, you here?

Yep.

How you doing?

What's going on?

Great.

Can you give us a brief?

Doing great, great to meet you guys.

Fantastic.

Is the office gonna change with this new fundraise?

I gotta ask. Are you guys gonna stay posted in the living room?

Do we have you Victor I think we might have lost you

Like where seems like we're having some technical issues. Okay. Well, we can hear it see and hear you now

Yeah, let me go far away from the Wi-Fi writer

I mean that is the issue with working at home. Complicated Wi-Fi.

You need the enterprise solution soon

now that you have the big series B done.

I know, I know.

It's coming very soon.

Yeah.

Oh shit, they are doing another meeting,

so I'm gonna steal Diego's room.

This is great.

I love getting the whole tour.

I love getting the tour.

Wait, wait, wait, you guys wanna see the office?

Yeah, please.

Yeah, yeah, let's just do a tour.

Anything that you can show us.

You can turn around.

Oh, okay.

There we go.

No API keys, hopefully.

Mexican music going on.

That's fantastic.

Hi, we're live.

Yeah, wow.

Hey guys.

How you doing?

Congratulations on the milestone.

Looking great.

Wow, you guys said, you guys,

we're not kidding about the living room,

but you've really built it out.

I love it.

That's amazing.

It's looking good. That's amazing

Looking good. That's good

Nice, uh, why don't you introduce yourself? I john john was gonna ask you that and then I cut him off. No, you're all good

Yeah, sorry, sorry about that no worries

Oh here we go, so

my my background my brother Yeah, like I guess on my background, like the TLDR is

I growing up, I was very interested into creative things of all kinds. I mainly had a music

band and I was doing from playing multiple instruments in the little studio that I created

in my house to producing music,

mixing, mastering, like learning about all of these

processes around music production.

But through my music band,

I also got super interested on doing photography

and like doing different kinds of content

for that music band.

So that way I explore like many different things

from graphic design, 3D, graffiti art.

I also had like a big passion for that.

And at some point I was, that was in 2015.

I was in, I was just like, I just finished high school

and I didn't, I was not sure about what to do after that.

And I had like two options in front of me.

One of it was go and

do classical guitar studies at the Conservatory of Barcelona, at the Conservatory of Guitar

of Barcelona. And the other one was doing something around computer science or physics.

I really liked math. And I guess what I like about math is kind of like the challenges

that it poses and like the interesting. Yeah, like I guess I like, I love challenges in math, put like a lot

of challenges in front of me.

But in the end, I found like this middle ground on this degree that it was called audio visual

systems engineering.

It was kind of like this degree where they showed you how a microphone works, how MP3

encodes audio, how MP4 encodes video, et cetera.

And that's where I met Diego, my co-founder.

That was like 10, 10, 10 years ago.

He ended up in that same degree following kind of a similar story.

In his case, he came from having a lot of interest in film and a lot of

interest in 3D as well. But also he also loved programming

and he also loved engineering.

So we both ended up like in that degree.

And on the second or third year I got introduced into,

I mean, first of all, I loved coding.

Like right after getting into the degree, I loved coding.

Found it like extremely creative.

Later on I found about AI.

I was mind blown by deep learning,

just like the fact that you can have these neural networks

learning by themselves from data and being

able to do such complex tasks was very interesting to me.

And when I discovered about GANs,

that they were very early models for image generation,

that's when I fell super deep into the rabbit hole.

And I ended up like reading a lot of papers,

doing a ton of implementations by my own

from all these papers that they were out there

back when everything was open source.

And ended up-

The good old days.

The good old days.

The open source days.

Do you have a first question or?

No, go for it.

20 million users, absolutely massive.

Congratulations.

Where are you seeing those folks come from?

Is it consumers just having fun?

Prosumers who are maybe doing

little contracting work, monetizing

their creativity on social networks?

Or are you already in the enterprise or all three?

All three.

I think that up until recently,

there were like two very well-defined blogs of users.

One of them, it was the consumer type.

It was people who,

this technology gave them a zero to one

when it comes to creative freedom

or to like enabling them to create.

It's people that didn't necessarily come

from a creative background,

but they had a lot of joy out of expressing

their creative ideas using this technology.

And they were paying for the subscription

almost in the same way that you could pay for a video game

or that you could pay for a camera.

Then we had the professional and the professional

it was that user that did have a creative background

and that he was using our technology

up in our platform to speed up some of their processes.

These are speed ups like variety,

depending on the industry.

Like you would see architecture studios coming to Korea with very low

resolution renders and using our enhancer to get these renders up to 4k

resolutions with very crisp textures, or you would see game designers coming to

our real-time tool putting a bunch of ideas around characters and being able

to create prototypes for some characters that they were designing.

Can you talk about just general adoption? So during the sort of like Studio Ghibli moment,

it's still top of mind. We saw a lot of people that still weren't aware, they had no idea how

these images were being created. John and I think that some people thought it was like Snapchat

filters or something like that. Can you talk about just like consumer sort of awareness and adoption broadly? You

know, are you guys still finding people every single day that are just sort of like completely

new to this sort of new image generation models or, you know, what do you think the broad

consumer awareness is today?

I mean, I was, I just came two days ago from a short trip to New York.

And I feel like that, that trip to New York made me realize how deep in the

bubble we are here in SF.

Like, uh, I think that I take for granted that people know that nowadays you can

generate images with

artificial intelligence and that's not the case. Like I think that we haven't, we haven't reached,

I wouldn't even know what's like the percentage of like reach that we have had right now,

but it's definitely very, very small. Like this technology is still nascent. People like us are

trying to make it intuitive and usable for really anybody

to just like grab a phone type a URL and be able to create an image very easy.

But I think that people still need to know that this is even a possibility.

Like I think that they just don't even think that some of the problems that they have

when it comes to marketing or when it comes to doing product design

can be solved today by artificial intelligence.

So I don't know if I'm the best one,

like if I'm the best person to have like a good sense

of what is a core adoption

because of how deep we are in the asset bubble.

Yeah.

From my experience that I've had in New York,

I don't know, like I have this fun story

that I was on an Uber and the Uber, like she just like saw that I've had in New York, I don't know, I had this fun story that I was on an Uber, and the Uber, she just saw that I was talking

on the phone in Spanish, and she was from Puerto Rico,

so she started talking with me and asking me

where I was from and what I was doing.

And this woman, she was selling

a sort of beauty products on Instagram.

And I saw it, and she started asking me,

oh, so can I use

your tool for doing like this product photography or can I use like all of these things? And

she was talking, I was like, yes, you can do it, but you need to go through a process.

It's not like some magic thing that you like go there and like, DIA does everything for

you. You need to go and train a model with your product. After the model is trained,

you go to the image generator.

There, you create all the assets that you want.

And after you have this workflow in mind,

after you have this workflow in place,

you can generate as many assets as you want,

and your workflow is gonna be extremely optimized.

How do you think about prompt engineering long term?

Is it, I remember a year and a half ago,

maybe a year ago, everybody said every company

like prompt engineer is gonna be this new role.

And now it feels like it's getting easy enough

to prompt a lot of these tools.

I'm sure like Korea that maybe it's just not necessarily,

maybe it's a skillset, but not necessarily a job.

But I'm curious how you think, do you think that prompt engineering will still matter

in five or 10 years or it'll just be super intuitive?

I mean, from engineering at the end of the day, it's just like being able to communicate

your ideas in a clear way with like this technology, you know, like we have like this AI model that can understand language and that can do things.

And from engineering, it's just like the way that you tell this knowledge that we have

encapsulated how to do things or what exactly to do. So at the end of the day, it's just managing.

And I do think that this feels like a new way of doing software.

And I do feel like this is going to, like in the future, most software that we see out there has been created by a very big percentage through prom engineering, through steering AI models towards whatever you want to accomplish.

And I see this on the visual space.

Like I see us building Creon in the future

more and more through instructions.

I see our users working with our platform

more and more through instructions

rather than through just like,

like typing a program and just getting an image.

I think that the Disney model from OpenAI kind of shows that.

Yes, speaking of the new OpenAI model,

it seems like they've evolved

the actual underlying algorithm.

It's not purely diffusion-based.

Are there new buzzwords or keywords

that have you reverse engineered

any of how they're doing that? Because it seems like

there's a number of steps like they're actually transforming the prompt, there's some reasoning

in there, the image loads top to bottom, which we haven't seen before mid journey kind of diffuses

everything from blurry to crisp, just the whole image at a time, it seems like they're doing some

sort of blocks or line by line rendering. What can you tell us about how that system actually works?

I don't have a, I mean, I have some intuitions,

but I'm not like super, I don't have high confidence

on how it works.

It seems like there's some outer aggressiveness going on

and we have already seen similar things

with crock image generation.

But I feel like to me, what it's really game changing

about this new image model is the, croc image generation but I feel like to me what it's really game changing about

this new image model is the game is like very similar to what we were like

talking about before like this if this is an image model that is able to reason

and it's able to understand instructions like it's able to understand here's like

the picture of my dog turn it it into Studio Ghibli.

And this is something new. This is something that previous diffusion models were not good

at. The diffusion models are good at, you have a text and you can generate an image

that kind of represents that text, but it's very hard to have them reason and to have

to think about what you want to do and what is the instruction that the user wants and

how to accomplish that goal.

Yeah.

Yeah, it seemed like there was like everything

at Style Transfer should have been

plus the latest and greatest in diffusion models.

They really packaged that up very well.

And so I think that's why it broke through.

But anyway, congratulations on the round.

Thanks so much for stopping by.

And thanks for the office tour, unexpectedly.

That was really fun.

But we'll let you get back to work.

I'm sure there's so much to do.

Yeah, give our best to the whole team.

And we'll talk to you soon.

Sounds great.

Thank you so much for having me.

Thanks a lot.

Talk to you soon.

See ya.

Bye.

Very interesting.

Nice.

We got Leaf coming on from public.com.

I'm curious if he's been sleeping at all.

It's a wild time in the market.

He has some interesting data on what's happening on public

because that's where people go to trade,

multi-asset investing, industry leading yields.

They're trusted by millions folks.

You've heard us do the ad reads before,

but now we have Leif in the studio,

breaking it down for us and we will bring him in right now.

How you doing Leif? Welcome to the stream.

Boom. What's going on? Great to finally have you. Nice. Let's go. I had my caffeine already so

that's why I'm like, good. Fantastic. Good. Somebody was commenting yesterday about our

caffeine consumption. Oh yeah. Yeah. it's easily, easily 500 milligrams plus.

Oh, yeah.

John, that's 500 milligrams during the show.

Yeah, but he's like built like a horse.

So he can take it.

How are you doing?

We were just joking about whether or not you had slept at all the last week.

I know it's been busy. You know, I'm sure it's been a busy time for at all the last week. I know it's been busy

You know, I'm sure it's been a busy time for you and the whole team

It's been busy, but our system have been up at least compared to other folks. So that's great

Yeah, that's good

Walk us through

Some I mean, I'm mostly curious to hear

You had shared on X yesterday about how there had been more buyers

than sellers over at least in certain moments

over the last week.

Maybe break down that data point

and then we can talk about some other stuff

that's top of mind.

Yeah, I mean, generally speaking,

just like a mini step back is like,

this generation of investors, like called especially millennials, like man, they have been through market cycles like

crazy in the past five years.

Right.

And or even just like through their lifetime.

And I even saw some of some like some meme on on X the other day of like millennials

experiencing the fourth once in a lifetime opportunity of a drop in market, you know? And I think especially like the March 2020 drop where like Circus Breakers

hit and so on is still in people's minds. And I think that specifically because you saw a lot of

individual investors actually also making money on that. And I think that has stuck with a lot of individual investors actually also making money on that.

And I think that has stuck with a lot of people. And so generally speaking, this behavior of buying the dip is a little bit

retail investing culture now.

And so whenever you see these massive drops, this is really when we see

some of our best days.

Yeah.

My reaction-

Yesterday was one of our record days in just deposits, for example.

And yeah, but yeah.

Yeah. Well, my reaction, the stock market was down 5% back-to-back days. And I was just like,

what is everyone complaining about? We're not even hitting circuit breakers. This is not that

crazy to me because I remember 2020 and it was way crazier. But of course, it's very serious.

Can you actually break down the mechanics of what exactly

is happening and what truly triggers the circuit break?

Yeah.

I don't have the exact numbers in front of me,

but it's essentially just if it drops too quickly

to specific thresholds, I believe it's 7% and then 10%

and 15% or so, essentially they pause

the markets.

And that didn't used to exist in the past, right?

And so it's essentially like a little bit of like a safety trigger, like a speed bump

to make sure that investors can take a breather when these markets start to drop too quickly.

Yeah. In Japan, don't they have lunch break in the middle of the day? investors can take a breather when these markets start to drop too quickly.

Yeah. In Japan, don't they have lunch break in the middle of the...

They do. Not just in Japan, other countries too. Yeah. Other countries too. I love that.

But yeah, it makes sense.

I mean, a couple of years ago, when the algorithmic trading got really popular,

there was like the flash crash.

I think the market traded down like 20 percent in like two seconds

and then went back up.

And yeah, obviously, you want to avoid that.

What about overnight trading?

You always hear, oh, you're watching the futures market

and it seems like somebody has an edge here

that they can trade before the market opens.

Is 24-7 trading coming to America?

We've heard some rumors.

Is there a way to get in on that action?

Generally speaking, I think it's definitely coming. It will also come to public at some point.

Right now, we essentially have 4 a.m. to 8 p.m. But the thing that you have to think of is that each trading window has its own participants and its own liquidity and execution venues.

And so think of it as like this, the regular opening between your 9.30 and 4.00 p.m., that's

the most liquidity.

It's when like most people participate.

You could call that the healthiest time in the market in theory.

Then you have essentially pre-market and post-market, which is, you know, 4 a.m. to 9.30 and, you

know, 4.30 to 8 p.m.

And then you have overnight, which is like the new thing. Overnight right now

there's essentially only like one major player who drives the liquidity for that and what happens

there is that because you have only one player you have a lot of like, or like, yeah, if you have not

as many platforms participating yet.

And so you can have these moments where there's a lot of kind of unilateral flow happening.

And that's why in the overnight markets, you often see certain stocks just suddenly rally

also on.

And that is a little bit, I don't want to call it fake, but it's a little bit like,

it has these wild swings, because the types of people that

trade in those times of the markets and it's a concentrated liquidity pool.

And so, you know, these swings just happen, you know, way more dramatically.

And so you often have these moments where like in overnight, a stock goes up and you

see on Twitter, everyone's like, I'm sorry, on X, everyone like posting the screenshots

of like, oh my God, you know, Palantir is going nuts right now over the company.

And then suddenly like 930 market opens and it goes, goes down and everything kind of

normalizes again.

Right.

And that is really just because each market window has to own participants and their own

pools of liquidity.

And so you kind of have to take a little bit with a grain of salt.

Like, can you play that?

Maybe.

But there's always this unrest there as well.

Can you talk a little bit about information diets?

And really, I want to know what events that are predictable,

not like Trump imposing massive tariffs all of a sudden on Liberation Day,

but what can we count on, like clock clockwork every single day to be the highest volume

day of the year? Is there a Super Bowl of stock trading that happens, whether it's earnings day

or jobs day? What are the big reliable sources of high liquidity in the market?

I don't know if I have a good answer there. My gut

reaction would be just from internal measures like Monday mornings because

you have a lot of cute orders from the weekend and stuff like that.

Yeah, makes sense. It's executed at the open. Okay. Because not everyone will

trade pre-market and stuff because spreads are wider and all these things.

But specific days, not really sure to be honest.

Maybe like big tech earnings too is kind of a season for that.

Generally speaking, it's always like, it's often just driven by market events,

right? And at the end of the day,

people will trade when they see opportunity.

And if you can predict that let's start a hedge fund together tomorrow.

But other than that, you know, it than that, it is driven by these moments.

We have good days when the markets are in the news, no matter which direction. But as long as the

markets are in the news, we have good days because people can inspire it one way or the other.

So in a way, trading volumes for companies like ours are a little bit like competing with any other thing

that competes with attention,

because if markets are in the news,

you get inspired by something and that might drive action

and that's what we see.

What do you see from a demographic standpoint?

I'm curious, the public obviously offers access to bonds,

which it was probably good to be in bonds

if you sold last week before Liberation Day.

But you see a lot of demographic differences,

sort of like Gen Z's basically like bonds for me

are just like GameStop, right?

Like I always know it's gonna be worth something.

Yeah, it's a store of value.

It's a store of value, right?

But I'm curious if you see sort of pretty specific activity

across different demographics in terms of interest

in these different types of assets.

Yeah, I mean, straight up bonds always feel older.

Just from the perspective of the older you get,

the more you're like thinking of preservation versus growth.

But then I think what's interesting now is that,

so we've launched multiple yield accounts essentially. So you have your high yield cash,

which is similar to a savings account, you just get your yield and it's variable based on interest

rates and such. Then you have your bond account, which is essentially like a basket of corporate

bonds underlying. And then you have your treasury account, which is like US government treasuries.

And those kind of simplify the investments into bonds because

you just deposit money, earn yield, it's like very simplified and just like you don't have

to like pick certain bonds and stuff like that.

So what we've seen is with that is that a lot of people are using those to just put

money into the markets waiting for these moments of opportunity.

So what we've seen the last few trading days essentially is that people

cycle out of the yield accounts and into stocks and ETFs because they essentially had this cash

lying around and were like, okay, you know, I think totally what we've been hearing a lot is that

like, hey, after Trump was elected and the market started ripping and there were all-time highs and

a bunch of things going on all the time that there was also a bunch of individual investors who were essentially

feeling like, oh, I might just buy in the top right now.

And so they put it into these yield accounts.

But then also, the minute you saw things drop the way they've done now, they've basically

cycled it out of the yield accounts into stocks and ETFs specifically.

So you're seeing younger generations using it less

as a, hey, I'm going to now actually hold the bond

to maturity 10 years from now, and more use

like these account tiles that we've created for just

like earn some yield on your stuff

until you actually see other opportunities.

Do you think AI is already helping retail investors better

understand the companies that they're investing in, right?

Every public company is putting out a huge amount

of information unless you're becoming just overly obsessed

with this specific stock.

It's hard to figure out what's important,

what should I be looking at?

What have you guys seen?

I know you've released products to help people leverage all of that data with AI, but I'm curious what you're seeing. What have you guys seen? Yeah, 100%. And like we obviously launched Alpha, which started off by just you can swipe

down on any stock, ask any question about the stock. And, you know, and that just created

this like bite size researching for things. And we've kind of fed the model with a bunch

of data that we already had from years ago. Like, for example, we acquired a company like

three, four years ago that was essentially a tool that turned all the SEC filings that

had, you know, custom company KPIs of subscriber

numbers and how many cars have Tesla shipped and things like that into more structured

data.

And then we use that structured data to train our models and such to make that very easily

accessible.

Now what has happened is that it's much more proactive than just you have to pull information.

And so the obvious one is what we call why is it moving,

which essentially if a stock is going in either direction very heavily, we kind of pop this card

on that page and tell people why this thing is likely moving right now. And then you can tap on

that. That brings you into a conversation with Alpha, gives you a more granular breakdown on that. And so it's much more the pulling versus the,

like much more like the pushing versus the pulling.

And I think that's also just generally where it's going.

But like what's awesome to see is that these like,

these like bite-sized contextual moments

where AI can be super fast,

where it's just really great at summarization

and can also go against biases.

So if we go for news stories, for example, we sort of say that QA multiple sources.

So we're not just coming from one source and pop it to you, but we QA multiple sources,

and then the summarization comes from the multiple sources.

And so there is a little bit of QA built in and a little bit of taking the bias out that

maybe one writer will have or something. Yes. Speaking of which can be helpful. Speaking of data

quality what what do you think. You know yesterday Walter Bloomberg shared shared some news that

that wasn't quite accurate and move the market you know trillions of dollars maybe helped

us avoid whatever it was. Black Black Monday. Kramer was calling

it. What do you think is do you think that do you think that there's any like solution

to that or it's just the nature of the Internet where now you have these accounts that basically

act. They publish they're basically like mainstream media except they just publish headlines.

They're not doing any journalism. They're not even looking at data. They're just sort

of like trying to be the first or second

or third big account that's like sharing a headline.

Is there any, what's the fix there, right?

Is there one or is that just the nature of the internet

where this sort of information breaks

and then markets are gonna react really quickly

and now retail investors are so ready to act on information.

You know, a good example is like,

if you just happen to be on X when Trump posted Trump coin

and bought 20 grand of it, you became, you know,

a millionaire within a few hours.

But I'm curious, like, if you've thought at all about like,

how, yeah, just, I don't know if there's,

I don't know if there is a solution, right?

Yeah, but I think it's, we always come back to

who are you building for and therefore what behavior

is your product inspiring?

And generally speaking, the way you design your product

will always have an impact on how people use it

and their behavior.

In our case, you can buy a Bitcoin, you can do options trades, but generally speaking, the way we've designed the product and the offerings that we have are more focused around

building long-term portfolios for people that want to compound their wealth over time,

for people that want to compound their wealth over time, all the fixed income offerings that we now have, et cetera.

And I think there are just certain design decisions

that impact in the end the behavior of these users, right?

And therefore, in the end, I think that is much more important

for people to make healthy investment decisions

than necessarily how they consume and so on.

But that behavior you're talking about is obviously not necessarily coming from the

potential wrong information from some ex-account.

That behavior is more cultural or how they were trained when they started being in the

markets.

And so I think that is much more the sense of like if the platform you're using is closer

to gambling, you will enter being more of a gambler automatically just based on the

design of how you were introduced to the markets.

And therefore, you'll be more prone to potentially react on these types of things because your

investing style will be closer to a gambler than maybe someone who tries to compound their wealth over time and you know

cycling money out of a high-car account into you know

Amazon stock or whatever because they see an opportunity that yeah both to then also hold it for long term and so

So I think that's much more than the the issue is sort of say then then then those accounts

I

Have a bunch of other questions, but I think we're over.

We'll have to have you back on very soon.

I know you got some big stuff in the works.

Thanks for coming on.

Yeah, I'm excited for the announcements.

This will be great.

We'll talk to you soon.

See you.

And we have our last guest of the show

announcing a $30 million Series B,

the smallest round of the day.

It's rough out there.

What is this, a round for ants?

I don't wanna talk too much trash.

I'm very, it's great.

It still gets a size gong hit.

But it is funny, we've seen a bunch of huge rounds today.

It's a good day in the markets.

The markets, the public markets are down,

but the private markets are ripping.

Let's bring in the founder and CEO of Arena AI. Today he's announcing a $30 million Series

B and introducing Atlas, an AI hardware engineer that is used by many of the world's most respected

and ambitious hardware companies. I'm excited to talk to him. Now, if you're there, welcome

to the studio. How you doing?

Boom. What's going on?

What's going on? Nice to see you guys. It's great. Would you mind just starting with to the studio. How you doing? Boom. What's going on? How's it going?

Nice to see you guys.

It's great.

Would you mind with just starting with a little introduction

on who you are, the company,

and maybe a little bit of your background?

Cause I thought the previous company

was really interesting too.

So I want to hear about that.

Thanks.

No, that's awesome.

Yeah.

So I'll tell you a bit of that company.

It's Atlas AI hardware engineer.

The company is called Arena.

We're based in New York.

Yeah.

Background.

I started out as an applied physicist. So I spent like a decade when I thought I was doing physics dealing with hardware engineer. The company's called Arena. We're based in New York. Yeah, background. I started out as an applied physicist, so I spent like a decade when I thought I was

doing physics dealing with hardware problems. Again, this was like a while back. You know,

switch gears went and did a brief stint through consulting. So, war suit for a short flash

of time over there.

And then-

Bring it back.

Yeah. It started right during that financial crisis too, which was a wild time to be starting

a job.

Wow.

That's insane.

But then, then sort of Miss Tech moved out of San Francisco.

The first company to your point was in 2014.

It was called Kimono.

So the idea was to make it really easy, I mean, to write a web scraper, right?

And it was pretty popular.

We had, we grew to 150,000 users.

We got bought by Palantir, which is where I met my co-founder.

We were there for a while and then started Arena in 2019.

Very cool.

Can you take me through the founding of Arena?

How did you settle on this to build?

It seems very on trend now, but you've been working on it for a couple of years.

What inspired you?

What was the early go-to-market, the first customer that you were talking to?

What does customer development look like?

All that stuff.

Yeah, totally. So just, you know, we had a bit of an interesting path here, I would say. It's

like a little bit non-traditional. We started, we decided to bootstrap the company. And so we said,

well, you know, if you think about like our view on enterprise problems, everything about the B2B

problem space is there's almost like a Maslow's hierarchy, right? Which is if you, let's say you've

had a job for two to four years and you're like, you've

encountered a certain group of problems, like you've encountered payroll, onboarding, communications.

But then if you've been there for a while, you're deep in that industry, you're almost,

you're seeing another set of problems, right?

And I think one of the things Palantir did so well is they were able to go so deep into

a customer for so long that they encountered problems for which there was very little competition

for.

And like previously you had consulting companies

kind of doing that.

So there's I think a whole host of sort of untapped problems.

And so our view is if we wanna tackle problems

that are really deep in an industry

that are really valuable,

we need to go really deep with our customer.

So that's been the philosophy since the founding days.

Instead of saying, we're gonna sell to other startups

and sell bottom up, the view is to start with a very difficult to enter customer start top down.

The origin of the company was actually more, let's say, less vertically opinionated.

We had added depth and reinforcement learning and transformers were like, let's go and apply

that for enterprise problems.

We were not as sort of like, our thesis hadn't formed as sharply as it had today.

And then we saw traction in a few different markets.

And post-Chat GPT, we were like, look,

I don't think for a small company,

playing in horizontal AI is really a winner's game.

But we found that there was this beautiful intersection that

went back to my days as a physicist, where

two different technical fields together,

with applied physics, electrical engineering, and AI. Now you have an interesting customer set where

you look at like a hardware test lab. It actually hasn't changed in a long time.

The incumbent competitors that are three companies from the eighties, you know,

it's, it's, um, weirdly the underpinning layer of technology on which all of our

software runs weirdly hasn't changed that much. Developing the hardware is like

stagnant and it's kind of surprising when you think about it.

Can you talk a little bit about like,

hardware engineering 101?

Are we writing Verilog?

Are we in CAD?

Are there other systems?

Like, what does the work look like?

And is this something where it's like,

it's managed on GitHub,

so Devin's gonna go off and write some code for you,

and we're just doing fancy autocomplete.

That's probably, I'm not trying to diss,

it's incredibly valuable if that's what it is,

but just concretize, like, what are we actually

talking about here for the folks

who haven't done hardware engineering?

Totally, right, so let's break it down,

let's take a simple example.

Please.

Let's take something like a drum, right?

Yeah.

We've got like, you've got like the mechanical shell

where you've got like your mechanical engineering,

CAD models,

stress-strain modeling.

Still a lot to do, but humans got pretty good at it.

We've been building physical stuff for a while.

We can screw things in, weld them together.

Again, not trivializing that, a ton of opportunity, but that's figured out.

Now inside, especially as you think about systems that are starting to go autonomous

or partly autonomous, you're like, we've had helicopters, now we have drones.

So what's the change?

The brains of this are basically like

a set of embedded systems, right?

So embedded systems effectively your computer,

the green motherboard like you've got inside,

except a whole bunch of them, right?

You've got like one that's operating as a sensor

and multiple different types of sensors.

So like an IMU for how you're oriented,

like temperature sensors, optical sensors.

So all of your sort of sensors, just like the body has, and then a brain, and then you

might have multiple brains, which might be on board again in our drone example, flight

computers.

And then you have actions that you take, like servos and actuators.

And you think about this, like inside that mechanical shell, you've got this almost electrical

skeleton, sort of like your own nervous system sort of wired together, right?

And at that layer, you know, to your point, there are two things that are happening.

One is all of the electrical connections to make that work.

And then for certain of those chips,

you're running code on board.

So to your point about the Devon,

so you might have an FPGA that's programmable,

you're putting code onto it.

And so that's sort of the,

we're currently at that inner layer.

We're currently at that nervous system

because there's this huge need.

And if you look at like the,

just the kind of labor markets for a second,

this is actually weirdly not surprising,

but kind of has profound implications.

The last 50 years, if you look at computer science

course enrollments, they're up by 90%.

None of us are surprised by it.

But electrical engineering course enrollments

are down by the same amount.

And so you look at it, we've got this huge,

we've got tariffs, we've got all that.

We've got a huge resurgence in American manufacturing, right?

And now you have all these intelligent hardware companies,

robot companies, space companies,

and you have this burning platform problem

where it's like, oh my God,

people haven't been studying this stuff.

And we're trying to now ship at the velocity

of a software company in a hardware space

where stuff can literally explode

without a workforce, right?

And so you understand.

Yeah, my favorite example here is you have Sonos,

which has made beautiful devices,

but they haven't managed to just get even the,

like the collective experience of using a Sonos product

is just completely brutal, right?

And then you look like, this is a company with like

Hundreds thousands of employees. They're public and it's not even defense

Like it's not critical that my speaker work like when I want it to play music, right?

It's annoying but it's not the end of the world and then it's like hey if that is hard in a controlled environment and a home

Yeah, and then we need to do much harder things

in these defense critical industries,

that should be a red alert.

Yeah, it totally is a red alert.

And that's where you've got customers screaming for it.

And at the root of it, you have this idea that,

you know, with software, we talked about Devon, right?

I mean, it's never been easier to write code.

Already, already weirdly Python

was an abstraction over like, you know, C plus,

it's not as hard as C plus plus,

it's gotten easier and easier.

And now like you're speaking in English

and like, that's amazing, right?

It's like the Star Trek computer.

And it's a beautiful environment

because code doesn't need to obey physics.

You just need to render in your browser, right?

Now suddenly you're making contract with nature,

as we know, you guys go outside,

like nature's unforgiving, man.

It's not like we fixed a bunch of,

we don't have space elevators, we don't have jet packs.

No, we have like TikTok, which is great,

but like what about all of that?

And the problem is we're encountering this physics.

And so each test cycle, to your point about the Sonos,

is like, great, I have an idea, I'm gonna prototype it.

Like, let me run it in my terminal.

It doesn't compile.

Great, I probably made a stupid mistake.

Everyone makes these.

But the cost of making a mistake at that speed in hardware,

like, worst case scenario, you get it wrong,

something explodes, but then even on the development cycle,

each time you're like, oh damn, the board was wrong,

I need to go and re-spin it.

That's like you're adding three months to the cycle.

And so these timelines and cost structures,

I mean, we all know how much the F35 program cost

and overrun, it's like, that explains it.

Like, I mean, there's a lot more that explains it,

but that's like a piece of it and an important piece of it.

Yeah, can you talk a little bit about

where you see the most value to be delivered

in the AI stack from,

it sounds like you're not doing pre-training

on a foundation model, is fine tuning important?

Is building a system on top of existing LLMs important? Are you doing

reasoning or is it more about UI and integration into existing systems? There's so many different

ways to create value in the stack right now. I'm sure it can be kind of overwhelming, but

how are you thinking about it?

Totally. And it's a cool question because our own thinking on this has evolved quite

a bit. I would say we started with a view that was much more, we kind of need to own all the pieces on the modeling side

and solve the hard modeling problem.

And we sort of realized like what's happening is

base cognitive functions are just becoming available

as an API.

So like vision is just gonna be available.

We shouldn't work on a vision problem,

like go fine tune like a YOLO or whatever,

VLM is your favorite.

You know, LLMs are maturing.

But what we do find is if you think about

like a person doing a work,

imagine like our objective as AI

is we're trying to get as good as like

a medium class person, let's say,

or like a junior person even, right?

And we unlock a lot of value with that.

If you wanna do that, now people do,

if we think about, you talked about reasoning,

and there's a sort of like notion for reasoning in LLM land,

but like if we just think about human reasoning, there's like a nuanced sort of like notion for reasoning in LLM land. But like, if we just think about human reasoning,

there's like a nuanced kind of like,

there are a couple of things that are special, right?

There's some sort of like,

especially in a formal environment,

like electrical engineering,

there are certain rules of the world

that we've learned over time that need to be true.

It's like gravity is 9.8 meters per second square.

You can't probabilistically learn that

by watching stuff fall in air and being like,

yeah, my ML model.

No, no, I mean, there's just some speed of light.

Like you're going to encounter that shit.

It doesn't matter if you're an ML model or like, you know, it's just real.

Right.

So there's some of these things with your hard constraints and, you know, where AI has

struggled is you tell an engineer something obviously wrong, they're never trusting you

again.

And they shouldn't, honestly.

Like you want to fly in a safe plane.

You don't want that happening. So there's a piece

here where it's like reasoning, but inside this sort of like

structured constraint, where there's a set of physics

constraints that apply that you sort of need A to win trust the

user, but B to work, right? The second piece is it's this kind

of multimodality where again, I'm not saying we need to build

from the ground up those models, but you need to make sure you're

getting really clean input.

That's input from... It's weird.

It's not like you're taking text input.

Text is, of course, a part of it.

I think the LLMs have gotten so good that it gives us an ability to really ingest a

ton of text documentation.

For sure, that's a piece.

Now, you're also looking at the thing.

You're looking at it visually.

You're looking at thermally.

Is it getting hot?

You're looking at readings from an oscilloscope. So you're in each of those things has

meaning to an engineer and the idea is can you now tease the right meaning from

that? And so a lot of our work is basically on that that data and fine

tuning side. How do we turn all of that into a package that can be fed in to a

set of models? And the other thing we found is, you know, a person is doing

multiple different pieces of work. A person might be saying, hey, I'm cross-referencing

in some data sheets.

What should this FPGA be expected to do?

Can this paint handle 10 volts at 100 degrees Celsius?

Or is this thing, am I going to short out

the most expensive part?

So that's almost like a kind of a text-based lookup.

But then you're actually running a test.

You're comparing waveforms.

You're doing math.

You're running simulations.

And so what we found is we're using different systems

to do the different, as agents, to different pieces

of the specialized workflow.

So you sort of have this meta agent that you're talking to,

and then you have these others that are sort of,

and the line blurs now between what's

an LM agent versus what's it calling, we'll call tools.

But those tools, if you'd talk to me in like November

2022 before Chad GPT, I would have been like, these are machine learning models and companies,

but they're just tools.

Now let's say, oh, I need a thermal recognition stapled with like, you know, the view from

the waveform.

That's an ML model.

That doesn't need to be like a 600 billion parameter model, but it's a non-trivial thing

to do.

And so you can look at this entire constellation

as being that sort of the product, if you would.

Got it.

One quote that comes to mind is, we were promised flying cars.

Instead, we got 140 characters.

I have to imagine that what you're building

and other tooling like it has the exciting potential to me

is sort of getting us out of this period of stagnation,

right, there's a lot of companies that are building,

there's companies building supersonic jets, right,

and they can use your tool,

and then there's all these other things

that we've yet to even imagine

or we imagined in science fiction,

but now we should probably think about building.

How optimistic are you around AI helping

to accelerate and help us achieve these science fiction

dreams that we've had forever but have never quite been

reality?

First of all, I love the quote.

It definitely speaks to my heart.

It's like if you look at it.

And it's an interesting question because it

can feel sometimes like reading the news,

like doom and gloom, AI is taking our jobs.

And it's like, you know, I'll go back to an example

that I lived as a physics grad student, right?

I spent a lot of time,

and I supposedly came in to do physics.

I was like, oh, I'm gonna do all this great

quantum mechanics research.

And I was basically like a mechanic and a plumber

for like 99% of the time.

I was like, this thing is leaking.

I think there's a water leak.

Oh, the screw got bent.

Oh, I was not doing it.

I was doing less than 1% of physics.

And that was the reality.

And I think that's a reality for a lot of us.

And so if you could take a lot of that away,

I think what it does is it changes, to your point,

what human ambition should be.

What could you achieve?

Let's say it takes 10 years on what human ambition should be. Like what could you achieve if, let's say it takes

10 years on average to build a startup.

In the past, like what we'd considered a SaaS company

is now just gonna be a feature in the future, right?

And I think, you know, original Silicon Valley

was about Silicon, right?

It was actually hardware-based.

And I think we're gonna see a resurgence hopefully

that my hope is, like what gets me personally excited

is one of the magical moments at my last company, Kimono, was you took someone who couldn't code and you said,

hey, wow, with this tool you could like write a web scraper.

And it was like, we just got the most amazing customer comments.

And I was like, felt this joy of enabling people to do something.

And you know, hardware can be intimidating.

You're in like a hardware lab even in college.

You're like, oh man, this is really complicated.

It's really, there's a high barrier.

Does it need to be that high?

We're seeing kids cheat on their essays with chatGPD.

That's a good thing.

We'll generate more stuff.

What if we could let them cheat at eLab with this?

Would we have more people going into hardware?

Can we lower that barrier?

What if you wanted to build a drone on the weekend?

You should be able to.

You should have Jarvis.

The goal is to be Jarvis, and kind of enable everyone to be a little bit

of a Tony star.

I love it.

In your announcement post, you highlighted five categories that it seems like you're

going after in the first initial rollout.

Semiconductors, aerospace, automotive, medical devices, and defense. Is that sorted by market size, like the burning need?

Just, do you like the way that it sounded in that order?

But I am interested to hear which of those

has the most immediate need or is the largest market?

Yeah, it's a great question.

So we started with semiconductors, right?

So that's sort of why we put it first,, you know, the most complex, especially we think about

a lot of what we do is electrical today, electrical engineering problems. And if we take the philosophy

of we want to be a little like Nike, start by selling it to the Olympic athletes and

get everyone to buy it. That was sort of the proving ground. And so we still have a few

semiconductor companies, you know, that we're scaling up to. But I think that's like, you

know, we all know the household names. It's a small set that are really valuable,

but they established the credibility.

That actually helped us.

We had a few great companies then come in inbound

based on that.

A lot of that was automotive and aerospace.

And it's interesting, I'm sure you think about like EVs

and like autonomous driving and aerospace,

you have a huge amount of that coming in.

Medical devices, we've got an early customer in there

and that's going really well.

There's a whole FDA angle to this

that we sort of need to work through, we're newer than that,

but it feels like the potential for impact is super high.

And so that's sort of like a little bit like the landscape.

I think we're seeing a ton of pull on the aerospace side,

especially as you look at that industry,

we're gonna have more stuff that flies. And then you introduce space to the mix and aerospace

and defense increasingly are mixed. So you look at these things, I think that's becoming

a unit in some way. And so it feels like there's a ton happening there right now. But yeah,

that's just a little bit, there was not a whole bunch of science behind that ordering.

Yeah, makes sense. I want to get your reaction to the tariffs. It seems like you're probably

an American company selling to a lot of American companies. Regardless of what you think about

the economics, it could potentially be a bull case for your company. How do you process

the news and what are you thinking about if it shifts your strategy at all over the next

using this series B over the next couple of years?

Yeah. We actually do have a couple of international customers too. Obviously, it's a huge impact.

The first thing we did was just call them because we're like, are you okay? Especially

look at these, the margins on something like a car have dramatically changed, right?

It's like you're doing some of the work here, you're doing some of the work there, some of it in America.

It's like, it's, yeah, there's a lot of American factories.

What percentage of the car is actually getting made here is a totally different question.

So you have a ton of like kind of a panic in the system, right?

But you know, you're right.

Like for us, it's been like it's accelerated customer pull and deployments.

They're like, oh no, like we can't go ahead

and have like that gross margin impact

and therefore have to do this with people.

We need technology.

And so it's actually a forcing function.

Like if part of this means that US sort of quality

and speed and sort of ability to manufacture

needs to get up really quickly,

and I think this provided the economic incentive for it,

and it's just not there, honestly.

This is just an accelerator, it's more fuel.

There's more urgency than there's ever been

on the customer side.

So yeah, I would say overall a lot of chaos there,

but net, I think from our perspective, good,

because it means there's a huge pull.

And this problem we talked about,

we talked about the 90%, the changes in those in those those people, like we suddenly need to do

a lot of this hard engineering in America. And it's this this finally put like a dollar

amount on how important that problem is.

How are you planning for kind of as AI technology gets better, it feels like we're firmly in

the copilot era. There's a lot of talk about, oh, electrical engineering

exam, I'm sure that these models have aced them

at the highest level.

And there's a prediction that AI will earn an IOI gold metal

this year.

And it's at like 50% on the polymarket.

And yet, I can't get AI agent to book my flight yet.

So how are you planning for

integrating that, taking advantage of what's state of the art and amazing and what AI does

well and then how are you building around the rough edges of the kind of innovation

jagged edge?

Yeah, you know, we think about this a lot because I feel like the question of defensibility

probably is going to come up much sooner in a company's lifetime than it's ever done before and so it's sort of like playing

with fire which is we want to be on the glide path where our product

automatically gets better as the Titans go to war and the foundation models

improve right like we just want to ride that wave but if we're just that's what

we're doing we're like let's get documents from the internet and help you

do cross-reference okay that's not, that is going to disappear super fast.

And so, you know, to your point,

it's tied in with like your math Olympiad

or physics Olympiad question, which is,

yeah, you've got your friend who's the genius,

who's like really good at tests, right?

And then you've got your friend

who I bet is a different person

who is really good at building stuff.

And usually they're not the same person somehow.

Like in my experience, there's always, there's your tinkerer friend

who didn't somehow get the A, right?

That tends to be the way.

And so we're not trying to pass the math Olympiad.

We're trying to be the guy who's tinkering

in the garage, right?

And so the tinkering in garage problem is very unsolved.

Like you look at AI's capability there,

it's like, it's a disaster.

But as the base cognition gets better,

you're getting better at viewer, yep.

To be clear, like when I think about the guy

tinkering in the garage,

my dad was a high school teacher

and he taught this class called Project Make.

And it was all about, it was some combination

of like wood shop meets electrical engineering

meets physics and you know,

you're making rockets and all that stuff. when I think about him solving problems it's like the tinkerer in the

garage and that he would just try a lot of different things and experiment and the beautiful

thing about AI is like I have memories as a kid of him working on one little problem like for five

hours like on a sunday like trying to figure something out, whether it's around the home or

in class. And like he's basically running like a series

of experiments, right? And so the potential of AI is like, run

every experiment at once, like in a simulated environment, but

like run like a thousand experiments in like, you know,

10 minutes, right? And like, when you start to think about

what that can do for like accelerating progress, that's the

most exciting thing for me,

because it's superhuman.

It's like the tinker in the garage,

but multiplied by a million.

Yeah, totally.

I mean, I want to get your dad signed up with the sort of,

we're working on like an academic edition.

I want to give him free access to that,

see if he could even, we're looking for feedback.

But I think that's-

He's retired, but I'll put you guys in touch.

If he's still interested, if he's still got a garage

That'd be great. Well, I mean, thanks. No, no, no. Here's the bar for the team

Five years from now. I want to be able to design our own podcast equipment. Oh, yeah

Yeah, the most cutting-edge, you know, we need h100s in these

Microphone I don't know why yet, but it sounds cool

I don't know why yet, but it sounds cool. Yeah.

Feel.

Congratulations.

I do have one last question.

How much do you attribute your incredible energy levels

to being a triathlete?

Do you think it gives you an edge as an operator?

I would hope so.

I do a lot less triathlon than I would like.

But I feel like it does.

Training the pain threshold is a useful thing.

I think it's just a useful thing in life.

Yeah.

That's awesome. Love it.

Well, thanks so much for stopping by.

Congrats on the milestone.

For the series B.

Thanks for having me, guys.

Appreciate it.

We'll talk to you soon.

See ya.

Have a good day.

Let's go to the timeline.

Justin Ross is quote tweeting,

did you see the Colossal company?

They have brought back dire wolves using ancient DNA

with their first born on October 1st, 2024.

They waited a couple months to make sure

that dire wolf was healthy and growing

over 10,000 years since dire wolves were extinct.

Can we do a deep dive on this?

I have done a full video and deep dive

on the company Colossal.

Remix, bring it back.

I was emailing with the company a while back.

I'll rekindle that connection,

hopefully have Ben, the founder, on the show.

He has a very funny collection of investors,

but some really great, George Church from Harvard,

fantastically renowned scientists involved in,

and they're working on cool stuff. So this post was put in the truth zone. People said, hey And they're working on cool stuff.

So this post was put in the truth zone.

People said, hey, they're not technically dire wolves.

They didn't really revive them using ancient DNA.

It's more genetic modification of existing dogs.

A little bit of controversial, but JD Ross chimes in and says, I don't care if these

are real dire wolves or not.

They're very cute and we should mix in golden retriever DNA and use them to hunt deer with us. And I couldn't care if these are real dire wolves or not. They're very cute and we should mix in golden retriever DNA

and use them to hunt deer with us.

And I couldn't agree more.

And you know where I would love to have a dire wolf

hanging out and maybe go on some deer hunting?

In a wander.

I wanna find my happy place.

Find your happy place.

Find your happy place.

Book a wander.

Book a wander with inspiring views, hotel grid,

and then these dreamy beds, top tier cleaning,

and 24 seven concierge service.

It's a vacation home, but better.

And, uh.

Go TBPN.

And I wanna go to Mike Noop, who we had on the show,

founder of Zapier.

He says, on the topic of AI is trained on all of humanity,

why can't it innovate?

A big question that we're talking about.

That question of the test taker versus the hacker.

He says, new ideas come from two places.

One, noticing similarities between two existing ideas,

new ideas in one area translate into another,

and two, logical construction,

new ideas follow from prior axioms.

One is easier and bounded,

and two is harder and open-ended.

And Dworkesh was talking about this,

like if you've trained,

a lot of scientific innovation just comes from somebody who's read so much

about the scientific literature.

They put together two random studies

and they find out that if you put those together,

you get innovation.

And then that's true in all sorts of different industries,

but specifically in just if you've read all the papers,

you've read all the books, you start making connections.

This is what David Senra does a lot with his show,

Founders Podcast, go download it.

But he says, two is harder and open-ended paradigm one can look a lot like career advice at the work to work at the

intersection of two fields because it's easier to become an expert in contrast being an expert in a single domain

Requires much deeper hierarchical knowledge and innovation requires novel in domain idea construction

this is the story of you story of Elon Musk working in space

and electric cars maybe having both of those knowledge sets

multiplies in some way.

Two, he says it's harder because you don't know

if innovation is blocked due to the prior axioms

not existing yet, or if you just haven't combined them

in the right way.

We want to build AGI that can innovate

due to the fact that one is bounded search,

leverages ML strengths like pattern recognition

and can bootstrap from human knowledge.

I think we will create AGI that can reliably do number one

well before number two.

Very, very interesting take.

And I just think it's like a interesting question

that he's clearly asking, like these AIs,

they're blasting through all the benchmarks,

they're doing all these amazing things,

but we're not seeing innovation come out of them yet,

or even you could think about like the joke test

as like you kind of need to be innovative

to come up with a joke.

It needs to come from something,

it needs to be new and fresh,

it's not just information retrieval.

The idea of like creativity is often just taking ideas

from two different places and combining them in some way.

And it feels like the models do that very well today

and that you can ask it to make me a song.

It's not doing it independently.

Just you have to sort of prompt it.

This was the genius of Harry Potter Balenciaga.

The human element there that made that actually go viral wasn't the AI

It was the idea that combining Harry Potter kids story with Balenciaga high fashion

That was funny

And then the AI just instantiated and I agree with you like the idea of

Taking two disparate concepts putting them together is where you get genius like take your best performing ad and put it on a billboard

With ad quick comm like that's gonna perform better.

And so go to adquick.com, out of home advertising,

made easy and measurable, say goodbye to the headaches.

Adquick basically took the amazing attributes

of online performance marketing

and brought it into the real world.

That's actually what they did, that's true.

I'm serious, we're not messing around.

You get a dashboard, you get all the different things

that you expect when you're running

a performance ad campaign online, on Facebook.

It gives you similar dashboards, but out in the real world,

and they do a lot to help you track the performance

of your out of home campaigns.

I thought this was a funny one.

We'll move on to Quake 2 has been fully AI generated

and replaced by Microsoft.

You can play it in a browser.

Every frame is created on the fly by an AI world model.

So they trained it on Quake 2,

had the algorithm or the AI play a ton,

generate a ton of frames,

and then just take the input from the controller,

output of the frames.

And so there's no game engine.

It's just input is what you're doing on the controller

Output is the game with visual fidelity and you can see where this is going. It's crazy. It's a lot of hate

Yeah, quite this quake dad quick dad

Dedicated to the committed to the bit says me. Well, they haven't released a new quake in like two decades

So this guy has been in the trenches forever

This is absolutely disgusting and spits on the work

of every developer everywhere.

Bold, John Carmack says, what?

Question mark, this is impressive research work.

And I love that because he is the creator of Quake.

And there was an amazing meme that was like

John Carmack holding a white monster being like,

oh, you completely replicated exactly what I did?

Awesome work. Based. And it's like the developer himself is like, oh, you completely replicated exactly what I did? Awesome work. Based.

And it's like, the developer himself is like,

this is cool.

But he did unpack it a little bit more

and so I wanna read through this.

He says, I think you are misunderstanding

what this tech demo actually is,

but I will engage with what I think your gripe is,

AI tooling, trivializing the skill sets of programmers,

artists, and designers, and that's real.

My first games involved hand assembling machine code

What a code this is why he's one of the greatest programmers of all time and turning graph paper characters into hex digits

Software progress has made that work as irrelevant as chariot wheel maintenance

Yeah, you don't want to be in the business of chariot wheel maintenance not a big industry today, but

Building power tools is central to all the progress in computers.

Game engines have radically expanded

the range of people involved in game dev,

even as they de-emphasize the importance

of much of my beloved systems engineering.

Maybe first person to say that,

systems engineering very, very hard,

and it's a huge time suck to,

I mean, when he built Quake,

he had to build the whole game engine.

He had to build everything, the idea of a floor,

that you can't fall through a floor or a wall.

You don't want to walk through the wall.

You have to write all that code from scratch.

Instead, now you just fire up Unreal Engine

and you get Fortnite out of the box

or you build in Roblox, right?

So he says AI tools will allow the best

to reach even greater heights

while enabling smaller teams to accomplish more

and bring in some completely new

creator demographics, people who don't know

systems engineering or even programming, for example.

Yes, we will get to a world where you can get

an interactive game or novel or movie out of a prompt,

but there will be far better exemplars of the medium

still created by dedicated teams of passionate developers.

And this is like the innovation concept,

this idea that the Harry Potter Palenciaga game

will be the one that goes viral and gets a lot of attention.

If you have distribution, you can capitalize on that.

But also if you have a novel idea that AI couldn't think of,

you will have a breakout success.

And so we'll focus more on game mechanics, game,

like there was this game, Bellatro,

that takes poker cards, and you're basically playing poker and trying to create like royal

flushes and whatnot, but it adds all these crazy mechanics on top of it.

It was a very simple game just designed in an engine, uh,

not crazy on a technical level, but the game design was so,

so incredible and so novel that it just went massively viral and like the solo developer basically,

I think he had a few people on his team,

just printed and became like the number one game of the year

or like of that quarter on Steam or something like that.

Well, what should you do if you're printing, John?

Pay your taxes, that's for sure.

Put your sales tax on autopilot.

Sales tax on autopilot,

spend less than five minutes per month

on sales tax compliance, go get started. They than five minutes per month on sales tax compliance.

Go get started.

They're back by what company?

Benchmark.

Five minutes a month.

You don't want to be bogged down.

And I mean, this is true.

You want to be focused on the innovation

that your company is doing.

You don't want to be dragged into a bunch

of unnecessary reports and sales tax.

If you're in SaaS, you can be thinking,

you're lucky stars that you can be thanking your lucky stars

that you're not a part of the trade war right now.

But take an opportunity to get your sales tax ducks

in a row.

25 states are now taxing software sales.

And Numeral helps you stay compliant.

So just do it.

Go to Numeral HQ and check them out.

Just do it.

And I think that's a good place to wrap up.

What do you think, Jordan?

Yeah, fun show, John.

Great show.

I enjoyed podcasting with you today.

It was fantastic.

Can't wait to do it tomorrow.

I know.

I was so worried.

I checked the date in my intro and I was like,

is it Wednesday already?

It's not, it's Tuesday.

We got three more days.

Glorious podcasting.

I know.

It's gonna be fantastic.

I have a feeling there'll be more news this week.

For sure.

The size gong hasn't rung its last gong sound the gong

The gong the gong is still fresh as long as we're

Yeah, it's great three beautiful three amazing series bees. We got all three founders on I think we did great

three of a kind guys

series be oh

Great, three of a kind. With Jize, a Series B.

Oh, I guess a Series B sized seed.

More of a pre-seed.

Anyway, three big, three 10 plus million dollar rounds

in the tens of millions.

Great to see it.

Lots of money flowing into startups that we love to see,

all working on very interesting things.

Remain bullish on America.

Me too, me too.

Anyway, thanks for listening.

Never lose faith.

We will see you tomorrow.

Have a great afternoon.

Have a great afternoon.

Cheers.