# Technology

**Date:** March 25, 2025
**Source:** https://podscripts.co/podcasts/tbpn-live/darshan-shanker-pavel-and-delian-asparouhov-alex-konrad-jordan-schneider-willem-van-lancker-christian-garrett-at-carrynointerest-11x-controversy-robo-arms

---

You're watching TBPN. It is Tuesday, March 25th, 2025. I got it right this time. We are live from

the Temple of Technology, the fortress of finance, the capital of capital. This show starts now.

We got a great show for you today, folks. We got a bunch of call-ins. We got some breaking news in

the financing world. Companies are doing deals. We got- Deals are getting done. We got media

announcements. We got VR announcements. We got news about China coming on. We got- Deals are getting done. We got media announcements, we got VR announcements,

we got news about China coming on,

we got a bunch of people calling in,

but we also got some news.

I see you're enjoying some Lucy cinnamon.

It's hot today here in Los Angeles,

it's feeling like spring John.

It's great.

Well, what you take on Signal,

because the Trump administration,

apparently, I've heard all these defense tech founders

complain, oh, I gotta use Microsoft Teams

because my work is so important

and I'm saving the country, but it's such a bummer.

I wish I could use Slack.

Turns out they could just use Signal.

I mean, they all use Signal.

I guess.

That's very common.

Maybe you should just run

the entire organization on Signal.

Seems like you can just do it.

Let's run the US government on Signal and RAM. It seems just run the entire organization on Signal. Seems like you could just do it. The US government on Signal and RAM.

It seems like it already is running on Signal.

That's of course the news of the day.

It's just wild that I try not to follow any political news.

I try to keep my head in the sand on that kind of stuff.

But I did see their emoji usage.

Oh really?

I didn't actually look at the story or anything.

I saw this is a

tech story and that's the way we're treating it Trump administration was was

found using signal Atlantic's top editor said he was added to a text group in

which top US officials discussed detailed plans to bomb Houthi targets in

Yemen and with other US officials an extraordinary breach of security from administration

that had repeatedly vowed to clamp down on leaks.

Oh, that's why that's going viral.

Yes.

It's the fist emoji followed by the American flag emoji

followed by the fire emoji.

Very American.

Very American, not super tasteful.

Atlantic editor in chief, Jeffrey Goldberg recounted in a 3,500 word story published Monday American not not super tasteful at land situation editor-in-chief Jeffrey

Goldberg recounted in a 3,500 word story published Monday how he got a

connection request on the signal messaging app from someone identified as

Michael Waltz he initially believed the request was fake but Ray later realized

the account belonging to the US National Security Advisor was genuine after the

group discussed detailed plans for an attack on the Houthis a

Militant group that has carried out numerous attacks and commercial vessels in the Red Sea

Goldberg didn't publish the actual plans in the article

But he said defense tech defense secretary Pete Hegseth at one point shared a post that featured

operational details of forthcoming strikes in Yemen including information about targets weapons

The US would be deploying an attack sequencing. Hours later

the attack went ahead. So it's kind of, I mean, there's a bunch of like bad takes about this. One is like, oh, signal got hacked.

That's not what happened. They literally just accidentally added the wrong person to the group. Signal was not compromised.

The encryption still works. The other kind of mediocre take or bad take was like,

the Atlantic shouldn't have posted this.

It seems fine.

It's the best possible marketing ever for Signal.

Because it's very quick, easy to understand,

okay, this wasn't a hack.

Yeah, it's a fat finger.

Yeah.

It's a fat finger.

Fat finger moment.

Yet validating the fact that some of the most important

people in the world, they're having the most important

conversations on Signal.

Yeah.

Shout out Moxie Marlinspike, founder of Signal, creator of a great NFT, as you saw.

Very fun.

And a great writer as well.

Moxie is a great technologist.

Anyway, Ben Thompson took the opportunity to write about this Trump administration group chat

through the lens of technology,

and I found his analysis hilarious and insightful.

It was great because, of course,

there's so many ways you could dive into this

as a political story, and I was like,

there's no way Ben Thompson is gonna write about this.

It's just like, it's so out of his wheelhouse. There's no way Ben Thompson is gonna write about this. It's just like it's so out of his wheelhouse there's no way. But you know here he says

I think this is a fascinating story with a very clear tech angle so up front let

me get the obvious caveats out of the way. Yes this was very stupid and

probably illegal. This goes back to the the way information is handled the

government, the Hillary email situation. Although the potential illegality itself

is an interesting tech story.

He says, start with Signal.

Given that Signal is a consumer app,

I saw a lot of commentary

decrying the obvious lack of security.

In fact, I think the opposite is the case.

Signal is actually the most secure messaging app.

I summarized the differences

between encrypted messaging apps in this update.

And he goes on to drop a very,

very detailed analysis of how encryption works in the different apps.

And it's fascinating. So I'm going to,

I'm going to take you through it because I really like it. And so, uh,

basically there are three kind of patterns for encryption. Um,

and he kind of breaks them down here. So iMessage is encrypted, uh,

Apple and presumably an adversary

cannot access your messages,

but the way it does this is by limiting

the maximum group size to just 32 people.

So every message in a group chat

is actually sent directly between the sender

and every person in the group chat.

In other words, when you send a message

to a 32 person group chat,

you're actually sending 32 separate messages

and potentially more if some users are using iMessage

on multiple devices.

Of course, messages are very small,

the internet is a very big pipe

and so it doesn't really matter,

but it's a fascinating idea

and this is the concept of fan out.

This is also the most secure implementation. There is both forward

secrecy meaning breaking one message like if you hack the encryption on a single message

it does not give you access to past messages and there's also something called self-healing

in encryption. This means that breaking one message gives you access to future messages

until you are offline for a single message at which point you have

lost the chain. So Signal uses what is called client-side fan-out. After an

initial back-and-forth exchange with everyone in the group, including the

exchange of send keys, which are the keys that unlock the encrypted messages for

everyone in the group, you send one message that is individually encrypted

for everyone in the group. you send one message that is individually encrypted

for everyone in the group.

This provides forward secrecy, but sacrifices self-healing.

However, because the send keys are themselves encrypted,

there is plausible deniability in that you don't know

for sure who sent a particular message.

Signal does maintain the structure of the group

in encrypted form on its servers to maintain

a consistent state for all users over time. WhatsApp is the most reliant on a

central server. This is the third type of encryption architecture that's popular

these days and they use what's called server-side fan out. So encrypted

messages are sent to a central server with send keys for everyone in the group

and then they are distributed by the server to everyone.

Part of this process entails maintaining the structure of the group centrally and while

there is a degree of plausible deniability, it does not go as far as Signal does.

And so what that means is that even though Meta cannot read your messages on WhatsApp,

they can basically map the network of who's in what groups and that potentially could be,

could kind of give you a way

if you broke one of these messages,

it's like, okay, well this person's in this chat

and this chat and this chat,

okay, we know who this person is

and we broke this single message, we're in basically.

And I would just say it's pretty amazing

how well Signal obfuscates the complexity

of what's kind of happening behind the scenes to deliver this very easy to use chat.

Yeah, it's remarkable.

It just feels like every other app.

You can't tell the difference between WhatsApp,

iMessage, and Signal even though they're using

pretty different architectures

from an encryption perspective.

And so Ben writes, while iMessage design

is the most secure and thus the least scalable,

you can't go more than 32 participants in a single chat,

which is something oddly I've never actually run into,

but I guess whenever there is a big group chat,

it's always on signal or what's happened for that reason.

I run into this in my neighborhood.

There's a neighborhood group chat on iMessage

and not everybody can be in it.

Really? Because there's only 32 spots.'s only kind of a Lord of the fly situation

Yeah, very competitive. It's great elbows. Yep, H away, you know, it's getting getting heated. It's great

But the problem with with iMessage of course is that it's closed source

Signals apps and protocol on the other hand are open source and there's no server component that needs to be verified

In other words, we have an Andy Warhol Coke scenario here.

Oh yes, of course.

Of course.

What's great about the country is that America started the tradition where the richest consumers

buy essentially the same things as the poorest.

You can be watching TV and see Coca-Cola and you know that the president drinks Coca-Cola

or in our case, diet Coca-Cola.

Liz Taylor drinks Coca-Cola and just think, you can drink Coca-Cola Liz Taylor drinks Coca-Cola and just think you can drink Coca-Cola to a coke is a coke no matter the amount of money

You can't get a better coke than the one the bum on the corner is drinking all the cokes are the same and all the cokes

Are good Liz Taylor knows it the president knows it the bum knows it and you know it too. I do love that philosophy

I always thought about like I've probably seen Jeff Bezos' favorite movie.

And I think that's just like really cool.

That's beautiful.

It's beautiful.

Although Jeff Bezos is listening.

He's like, John has not seen my favorite movie.

Yeah, yeah.

I have movies.

I bought.

I bought.

I have hundreds of movies.

He actually does because he owns Amazon Studios.

Even the individual actors don't haven't seen the movies, right?

They were, it was filmed in pieces and assembled. You have to't seen the movies. Yeah. Yeah, they were it was filmed in pieces

Yeah, assembled to take out the editors. He really relish mom that he has his own

Like oh yeah and inception to you ever see it John because I made it I spent a billion dollars

It's better than the first

He has his own award. Yeah, you know Godfather 4 it was amazing brought me to tears. It's a classic

It's a classic. Okay, rewatch it

Constantly twice a year twice here and John you're never getting to hold on it. Anyway, Jeff

Okay, anyway Ben Thompson goes on to say, so it is with encryption,

there isn't really a more secure messaging protocol

than Signal, even if it were designed by the NSA.

What is interesting is that the last bullet point

in my excerpt, one way in which WhatsApp in particular

could be compromised is if the server,

which orchestrates the chat,

were to insert a silent participant in the chat

when it was established.

This silent user, which could be obfuscated

in the user interface, remember WhatsApp is not open source,

so the WhatsApp code could say,

if Mark Zuckerberg joins the chat,

just don't show that to anyone, in theory.

I'm not, there's no allegations this is happening,

but it's possible.

And so-

If it's possible, it happens.

It happens.

But you see that Rogan clip of Antonio Garcia Martinez,

where Rogan's like, the phones are listening to us, right?

And Antonio has to be like, no, like I worked at Meta,

like trust me, like if we were listening to your phones,

like the ad targeting would be better.

And Rogan's like, but they're definitely listening, right?

It feels like they're listening.

But Antonio Garcia,

paid boss. Paid off paid off by a great founder,

you know, just recently exited.

Do you need to put on the tin foil for this?

Yeah, is he the guy that goes on JRE

and is meant to say the phones aren't listening?

It's somewhat believable.

Yeah, somewhat believable.

We'll see, we'll have to put the screws to him.

We're not gonna go, I'm not gonna take it this far.

Everybody will.

You don't need to get clipped. Save that for later not gonna go. I'm not gonna take it this far everybody will

Anyway, the reason I bring this up is because that's kind of what happened here Goldberg was added to the chat Although albeit not silently there was certainly a notification about his addition and he would have been publicly listed as a chat participant

However, if you read the story Goldberg was added at the same time as a bunch of other participants were added,

and it seems like no one noticed.

That means he effectively operated

as a silent participant and thus saw all the messages

until the time he exited the chat.

So fascinating.

Anyway.

What was your takeaway?

I mean, my takeaway is this kind of fat finger move

would be ruinous for most.

Most boys group chats.

Most friend groups.

Most friend groups.

In the entire world.

Yeah, I guess the message to the listeners is

take a scroll through your signal group chats,

make sure you don't have any silent participants

you accidentally fat finger into the chat.

He goes on to talk about transparency versus security.

What is perhaps the most surprising detail

about this episode, however, is that the violation

was not about security, but rather transparency.

In fact, the official policy of the DoD

is that officials use less secure means of communication

from a Pentagon memo about the use of text messaging,

effective immediately when conducting government business

of DoD users of government-owned mobile devices

and non-government-owned devices.

You have to use Microsoft Teams chat for text messaging

as the fully designated managed DoD mobile enterprise system

for use on government-owned mobile devices.

Microsoft Teams chat will be available

as a managed application, blah, blah, blah.

So basically they want you to use Microsoft Teams.

Shout out Sacha Nadella for getting that deal done.

But it's not end-to-end encrypted.

The DoD's primary concern is not message security,

but record retention.

They want to have all the records.

They don't want it encrypted.

Anyway.

Yeah, this is one of those things,

the challenge anytime you're trying to roll out

new software to a team or get a team to adopt software is the sort of like people by default

will flow to the platform with the least friction,

which is like what they're already using.

So we see this, we have Slack,

we don't use it for the show.

Right, we just, iMessage is just still the default.

And I'm sure at some point we'll move some more.

I mean, we need to get more secure

with all the other podcasts that are attacking us

and trying to hack us.

Yeah.

Security, cybersecurity.

I mean, we've been talking about

trying to build our own version of Wiz,

hiring some Israeli guys to build that for us.

But this could be a good move.

Telpio.

Yeah, Telpio.

Yeah, we need the top guys for sure.

The top guys. For sure, to secure the security secure the story at all at all costs

Anyway, he closes by saying there are security considerations executive branch officials

Perhaps overstated their case when they wanted official records locked up forever

But are we really sure that we want ongoing?

Conversations to be happening on services that are any less secure than Signal?

Again, none of this is to dismiss the stupidity

of this particular case,

but that's why I find the story so interesting.

There are a lot more ramifications

beyond one military operation

that raise legitimate systemic questions

about how the government should operate in the digital age.

And it's interesting, yeah.

This relates to that other post we talked about,

which was that in, I believe, the UK,

there was a member of parliament whose chat GPT records

or AI queries were maybe like subpoenaed or released.

Freedom of information.

Yeah, yeah, FOIA.

And there's this question of like,

what is the value of our leaders being

able to have private conversations? Yeah.

Historically, it's been very easy. You know, Abraham Lincoln walks outside with

his top guy and just goes for a stroll and like no one else is listening and

they can weigh all the possible options on how they want to win the Civil War.

Well, we don't know at what point they developed robot birds that could sort of fly above political leaders

for conversation.

Well, I mean, the Nixon tapes was basically

the start of all that, right?

And he was getting wild in the boys group chat

in the White House, basically,

saying a lot of crazy stuff.

Well, so this is interesting too.

Further down in the article,

they talk about how there was an incident

called the Salt Typhoon Hack,

in which China had the ability to read

pretty much every SMS message in America,

which is why the US government advised citizens

to use end-to-end encrypted apps like Signal.

And that's why if you're on SMS,

specifically if you're not on iMessage,

you need to be sharing American propaganda

that is convincing to Chinese nationals and the CCP.

So when they hack you and they get it,

they're like, wow, capitalism is sick.

Yeah, China's equivalent of the CIA

is reading your messages and you gotta turn them.

You gotta turn them, exactly.

You gotta be like-

Because they're listening, so you gotta turn them.

You gotta post-

Hey, like it's a beautiful day today.

I'm gonna pick up my kids, you know, taking a football practice and barbecue.

What are you doing? Yeah. And it's just like multiple times.

Exactly. Yeah. Barbecuing, barbecuing. It's, it's a beautiful day.

What was your, what was your quote about, uh, uh,

Mark's failed to consider how making money with your absolute boys is fantastic.

Something like that.

You send a couple of SMSes across the Salt Typhoon hack

and it's gonna be peace all over the world.

Yeah, we should actually turn off iMessage on our phones

and just text each other SMS.

It is ridiculous that they were just spamming out

these government secrets.

It's almost like, I mean, they should have just put it

on a billboard, like at this point.

They should have just taken all of the instructions,

everything, they should have just communicated

through a network of billboards.

They should have just gone to adquick.com

because they have out of home advertising

made easy and measurable.

They could say goodbye to the headaches

of out of home advertising only on AdQuick,

which combines technology, out of home expertise,

and data to enable efficiency.

And AdQuick is very privacy oriented.

People are not gonna be finding out about your campaign

until you want them to.

That's a really good point.

When it actually hits the billboard.

Exactly.

So, yeah, just something to keep in mind.

We'll head over to Washington, we'll let them know.

Yeah.

If you wanna, you know, if you wanna.

If you wanna get your DMMS to the mainstream media message,

put them on at the right time. Just put them on a billboard. Yeah.

You could also, uh, if you wanted to talk with, with Goldberg directly,

you could just buy all the billboards. Yeah, exactly. I'm sure.

I'm sure it's possible to figure out we're not gonna dox him but

You don't need to add Goldberg to your secret chat you don't need to just to send a message exactly You can just you can just use a billboard for that, you know, etc

Anyway, should we move on to 11x? Let's do it. Talk about 10x engineers 10x spies now

We're talking about 11x a little bit 11x crazy name they took I mean well it's the the meme

You know take it to 11, right?

Anyway it's an AI SDR company that's embroiled in controversy after

Allegations from TechCrunch that they claim that they had customers that they don't have

And there are definitely two sides to the story.

So it'll be fun to dig in, not dead to rights yet.

Some Andreessen folks came out in support.

There's some haters on the timeline.

Interestingly, the scoop comes from TechCrunch.

I'm wondering, 11, you know, this one goes to 11.

Do you remember the movie Spinal Tap?

Yeah, I remember that.

That's potentially a deep Spinal Tap? Yeah, I remember that that's that's

Potentially a deep spinal tap reference. I always thought that this was just like affiliated with that club in Miami 11

That that could be that's probably it's probably like a spin up because they were they were getting into cryptocurrency

Employees, yeah, we could spend all day at 11. Yep, and we would never have to work

well, no, I mean it makes makes sense that 11, the club,

would incubate something like this,

because they need to text their high paying clients, hey,

do you want a bottle service tonight?

Yeah.

What's going on?

They have a pretty sophisticated outbound.

It makes sense.

Outbound engine, CRM.

Yeah, really, really increasing.

I mean, that's high margin stuff if they get them coming in.

I mean, they're not paying $250 If they get them coming in, I mean,

they're not paying 250 a bottle for Dom at 11.

Talk about it.

It's gonna be 5K.

At least.

Yeah, and so you gotta start using the AI sales reps

to just be hitting everyone that comes through.

Pounding the digital pavement.

Exactly, pounding the digital pavement.

Anyway, let's go to TechCrunch.

Last year, AI powered sales automation startup, 11X,

appeared to be on an explosive growth trajectory.

However, nearly two dozen sources,

including investors and current and former employees

told TechCrunch that the company

has experienced financial struggles

largely of its own making.

So their own investors are talking to TechCrunch.

Wow.

Numerous people in the US and UK told TechCrunch

that the situation has become so tenuous

that 11X's lead series B investor Andreessen Horowitz

may even be considering legal action, ayayay.

However, a spokesperson for Andreessen

emphatically denied such rumblings telling TechCrunch

that A16Z, they ain't suing.

Yeah, this story, it's interesting.

Like TechCrunch got the scoop,

but it didn't have a lot of meat here, right?

It's just sort of like a lot of like he said,

she said, former employee says.

I think let's read through the meat that is here

and then let's dig into the response from the founder,

some of the support from Andreessen,

and then I wanna talk about kind of the meta level

of where is it, you know, how much,

how much should you fake it till you make it, basically?

The contracted ARR.

Yep, that, and then also the logo stuff,

there's been a classic example of like,

oh, a guy from Google signed up for my service,

therefore can I just say Google uses my service?

You know, always been questionable.

So 11X offers a bot for outbound cold sales duties,

including identifying prospects, crafting custom messages,

and scheduling sales calls.

All stuff that's like very doable

within the current regime of AI tools and foundation models.

It's one of a number of AI startups in the hot area

known as AI Sales Development Representatives or AISDRs.

It was founded in 2022 by Hassan Sukkar.

11X said it approached $10 million in ARR

just two years after launch

and moved from London to Silicon Valley last July

and announced a $24 million Series A

led by Benchmark in September

and then very quickly followed up later that month

with a $50 million Series B from Andreessen Horowitz.

Three current and former 11X workers told TechCrunch

that most of its early customers took advantage

of break clauses in their sales contracts

to discontinue using the product.

Customers faced issues such as the email product

not working as expected or hallucinations

according to sources, very standard stuff.

Yeah, so I'd love to get a sense.

I don't think we're going to get it from this article, but a sense of was this contracted

ARR like, hey, you're going to sign up for a year or two, but you have a three month

sort of like non-paid trial that converts in?

Or were these customers actually paying?

I think they probably paid. And I think it's basically,

I think what the ARR calculation is, the gold standard of ARR is that

if you're counting it as ARR,

it by contract legally has to come in every single month

for at least 12 months.

And so it's okay to multiply that number by 12.

If you can break out of it at any moment in time, it's

annualized revenue. Yeah. And it's not necessarily recurring. You'd like it to be recurring. This is the case with my with

Lucy, like we have people on subscription. They're not locked in for 1212 months. Same with Rora. But it's helpful to to

kind of look at the subscription revenue,

multiply it by 12 and be like, yeah,

I can probably count on 10 million coming in

over the next year.

We have subscribers that are roughly worth, you know,

exactly this amount with a summit discount return.

But it's very different from, okay,

you have a ironclad contract

that would be very difficult to break.

Yeah, the big thing here is companies like 11X

and there's been a lot of them, they make these sort of really

big promises.

And I believe the potential is there.

But the issues that 11X customers,

as they're facing issues, like the email product not working

as expected, or the product just hallucinating.

And there's a company in my portfolio

that builds sort of similar agentic products

for another vertical.

And they were able to like get a V1 that was like magical,

like 60% of the time, which is not enough.

And so they then had to spend like almost a year

kind of rebuilding the product

and now it's working really well.

But the issue is like you go and you sell like an air table or zoom info on something like this. And

if you have an outbound sales agent that's magical 60% of the

time, but 40% of the time it hallucinates. Yep. That is not a

magical product, like you're going to piss off customers. And

it's like the fastest thing that somebody is going to turn off

because they're, you know, gonna, it it's just it's so rough because I mean obviously

I think everyone's a believer in the agent paradigm

but it were clearly in the centaur era where

We've talked about the centaur chess how for a long time a human plus a chess engine would defeat both the best

chess AI and the best human and I I would just imagine that, you know,

like what Devon and Cursor are doing for programmers

where they're not fully replacing the programmer,

they're more just like an extension of the programmer.

And even the way most people use Chatchie PT,

it's very interactive.

I send it some bullet points, it turns it into a paragraph,

I edit that, I change that.

I could imagine a product in the AI SDR world

being super helpful even if it wasn't agentic

because 60% of the time it writes me a great email

and I can just click send but I'm still reviewing,

I'm still in the loop.

The reason we've seen so much traction

on the engineering developer tooling side

is that developers can see the agentic product

make a mistake, they can help correct it,

and nobody's impacted other than the developer.

Devin sends in a GitHub pull request,

and then a human reviews that most of the time.

I mean, I'm sure you can just say merge,

but most people probably review the code,

at least a little bit, or run a test suite against it.

And if you don't have a test suite against it and if you

don't have a test suite or a code review process for the emails that are being

sent it can get very spammy anyway this is a funny this is a funny line so

there was some internal drama to employees described an art arduous

stressful work environment even for those who embrace hustle culture so even

if you love working hard,

it's gonna be a stressful work environment.

So anyways, gotta call that out.

They're also in Hotwater for maybe

fake in customer endorsements is what's left here.

I think using logos a little bit too aggressively.

It seems like what happens is they had

some big companies sign up,

do these sort of whatever the deals actually look like,

churn and then they kept putting them on the site.

I think where this got, I'm sure, annoying for Zoom Info

is that Zoom Info I think also has like a competitive-

They have a competitive product, yes.

And so Zoom Info must have signed up at some point or someone from zoom info signed up and

11x used the zoom info logo along with other multiple companies on their website to show hey

We're a real business

We have a lot of great customers and zoom info said we did not give them permission to use our logo in any manner

And we are not a customer. So rough there.

And this happens in ad sales.

Yeah, it's been pretty aggressive.

I'm sure you've seen this with like Ridge.

There's been a lot of,

I don't know if it happened to Ridge,

but there's a lot of agencies that will do like one campaign

and they'll be like,

well, we're responsible for all of Ridge's growth.

Yeah, we scaled this company, we scaled that company.

And then the CEO will get on and be like,

hey, look, we were fine working with you,

but give our

team some credit here. Like we worked really, really hard.

I have that happen all the time. Still people I'll reach have somebody reach out to me and

they'll say, Hey, so and so says they did something, a party around the party around

branding. And I'm like, I don't know their name. I don't actually know. I was, I was

like a part of every process.

But yeah, so it sounds like they've been not just

putting the logo on the site.

They've been claiming it in sales calls

and now on its own AI dialer.

Well, were those sales calls hallucinated?

Because it's possible that this is all just one,

everything is just one hallucination.

And they're like, well, yeah, we just

told our AI to make a landing page

and threw some logos on there.

The website feels like what? Like it was entirely AI generated.

Yeah. If you've seen it. No, I haven't. It's like all AI.

Like, look at this. Like, like. Wow. It does feel like the.

Again, I don't want to dunk. I don't want to dunk,

I don't want to dunk on them.

They are digital workers.

So anyways, if you don't have anything nice to say,

don't say anything else.

Oh, they really like focus on like, it's a person.

Okay. Yeah.

Alice, Julian, Giga Chad.

Yeah, so it sounds like this blew up in their face

partly because ZoomInfo had been asking them for months

to take down their logo,

to stop using them in marketing materials.

And it sounds like they didn't listen.

I mean, Rowe is still on here.

You should hit them up and ask

if they're actually a client.

Do some journalism here.

Anyway, what I really want from them is an SDR

that's just an IFBB Pro,

because Julian looks great, Alex looks great,

but I want an absolute mass monster in a tank top

who can really sell some supplements for me.

That's the goal.

Apparently the CEO doesn't believe

in people taking holidays,

which we can't comment on that.

Ben, when did you request time off? Anyways, I thought this, this line was good.

And then honestly, let's move on.

There's a lot more under the hood.

A current employee said, wow, a current employee, you should probably leave.

Yeah.

Get on with your life.

One day there will be a documentary about this guy.

I do believe that's how scandalous he is.

So obviously, Sukhar pushed back.

He sort of went through a bunch of different bullet points

outlining how.

But yeah, overall, you don't see benchmark

in many companies that have this kind of story.

No, totally.

But this, again, the sort of critique of venture in

the last year and a half, two years has been companies are

growing so quickly raising so much capital, that they are

overestimating their traction. Basically, the idea of ARR is

now when everybody's saying, Oh, we got to 10 million ARR in six months,

then the pressure starts building up

where founders feel like,

oh, well, my competitor is counting contracted ARR

to raise more money.

And so that pressure just builds up

and these rounds are getting done really quickly.

And the faster a round gets done,

the less time there is to do real hardcore diligence.

And in many ways, I'm sure all their investors knew

that there were issues with the product,

but it was a bet broadly on the category and the team.

I mean, a lot of this comes down to the material threshold

during due diligence.

I remember I was using the same lawyer as Zenefits

during the whole Zenefits arc.

And we were doing a $20 million series A I was using the same lawyer as Zenefits during the whole Zenefits arc and

and we were doing a 20 million dollar series a with Andreessen and

Zenefits was doing a

500 million dollar series C or something like that and

My deal was taking forever in terms of due diligence. It was like such a beast. And I was like the lead on it.

And, uh, and I was like, Oh man, I can't imagine what it's like to do a $500 million round. Like

that must be brutal. Like ours has taken like months. It's been so much work, like so, so many

like checks on like this, this employment contract, this deal, this, this thing, get the FDA people.

It was a lot. Uh, and, and And from a legal perspective, it's actually easier

to do due diligence in a $500 million round

because you set the material threshold

at like 1% of the funding that's coming in.

And so you might say,

hey, we're doing a $20 million raise,

let's look at every contract that's over 200K.

Because look, yeah, if there's some employment contract

out there that's 100K liability and we get it wrong,

we'll just write it off, it's not a big deal.

But when you're doing a $500 million round,

all of a sudden it's like, oh yeah,

if there's a $4 million liability on the balance sheet,

we don't know about, like, who cares?

I don't know that, this might not be the actual numbers.

But when you're a small company and they raised a,

in 2023 they raised a $2 million pre-seed,

then a $24 million round in 2024,

and then immediately a $50 million round.

Like it's probably still a pretty small company,

and so if there's a contract out there

that's like pretty small, you might just be like,

well, like it doesn't really matter,

like we're not gonna dig into it that much,

it just doesn't make sense based on the scale of the company.

But-

Yeah, I do like how Andreessen and Benchmark

have both come out in support of Hassan.

I'm sure Hassan, like every founder, has made mistakes,

but hopefully, I'm sure he'll learn,

and the team will learn from this crisis.

But Joe had a good point

What they've built is remarkable the team product of metrics are world-class and they're attacking a market opportunity that rivals any have ever seen

And then Sarah Taville came out and said

One of 11 X's incredible strengths that I believe will compound for many years to come is the break that pace at which?

Hassan and the team move that kind of speed brings both opportunity and challenge, especially early on.

Yeah, this is a cool going direct addressing the news.

Clearly people are going to be talking about it.

He puts out all this information.

Also funny to dig into, they've raised 76 million

and he says, we barely touched our investment capital

and have nearly 70 million on the balance sheet.

And I mean, I guess it's only been a couple months,

like less than a year, so they're not burning a lot,

but it is interesting that like, yeah,

like even if the ARR is a little off or something,

or there's some churn, like they could totally figure this

out and like wait, they could wait like what,

based on their burn, probably like a decade

for like agents to get better and like LLMs to improve,

like as long as they can keep the energy in the team and like

Get through it like it's probably fine. The timing of this is fascinating in that tech crunch just changed hands. Yep, and

They decide yep

We're gonna just like immediately do a like an aggressive hit piece, which is

Exact opposite of what people have liked about TechCrunch.

TechCrunch, Adam Ryan talked about this on the show.

They talked about how he said that TechCrunch was the make your mom proud engine.

It was a place to launch companies.

And it's a weird position to be in to try to do investigative journalism and be a launch

platform.

Oh, totally.

And so again, yeah, I'm sure this drives a lot of clicks.

Yeah.

But yeah, it's kind of, yeah, it's just again,

it's an awkward place to be in.

Yeah, I mean, he does admit some amount of fault here

saying like, we regret not having a better process

to remove logos from our website more promptly after

Customers churn, but he's he says they've never put a customer on there who didn't pay

Yeah, it's a great clarification and that makes sense like yeah, you know updating front-end

It should be easy with AI

But sometimes stuff gets slipped and you forget that oh, yeah, they churned like we should probably remove them

And then also he says our investors are not suing us.

They categorically denied this to TechCrunch,

yet this rumor was included in the article.

And so a wag of the finger to TechCrunch on that one.

They should have been firmer on that.

But good luck to them, good luck to everyone building AISDRs.

And let us know if you're building an AISDR.

I almost said his real name,

but we're gonna have somebody named Carrie No Interest

on the show later today to just talk about

the AI sales automation market generally.

He's been somewhat a critic of SaaS,

but he also is actively buying

and transforming existing SaaS companies

and is building some stuff in the space himself.

So excited to have him on in a couple hours.

Yeah, and for Hassan and the 11X team,

I think they have 70 million on the balance sheet still,

something like that.

They are clearly going through like a tumultuous time

with this negative article.

They got to rebuild, they got to redouble their efforts.

And I think like the number one thing that they could do to really get through this hard time and accelerate

is just keep costs low, get on ramp.com. Time is money, save both, easy to use corporate

cards, bill payments, accounting, and a whole lot more all in one place. Go to ramp.com

and sign up.

Yeah. I mean, the strongest signal that 11 X could send market right now is getting Saquon to come in. That would be

fantastic. Basically, I thought you were gonna say the strongest

signal they could send the market is just putting out a press

release saying like, hey, we're on ramp now. Yeah, just hey,

we're taking everything seriously. This is serious

company and we are in a serious financial platform. Yeah, we

don't mess around. We don't mess around. But an even stronger signal would be getting say Kwan say Kwan's to our knowledge is invested in two companies

Yes, ramp and and Rol. Yes to

the third

Third yeah the trilogy of say Kwan investments if you're a founder in Silicon Valley

Like you have to be calling say Kwan right now to be number three. Yeah

in Silicon Valley, you have to be calling Sequon right now to be number three.

Yeah.

Give him Sharon.

I mean, every other VC firm that invested in Anderil or-

Get Sequon to invest in your company.

Go into debt if you have to.

Yes.

Every other Silicon Valley firm that's

invested in Ramp and Anderil has a ton

of corpses and bad investments.

Sequon appears to be just-

The guy doesn't miss.

Doesn't miss. Doesn't miss.

It's great.

Anyway, speaking of a ramp investor, Thrive Capital,

and AI, Thrive Capital is leading a new deal

in Wall Street AI startup, Rogo.

Is Wall Street ready to work

with artificial intelligence rights,

Natasha Moskrenos over at The Information.

Two of OpenAI's biggest investors think so.

Thrive Capital is set to lead a $40 million financing

into Rogo AI, an artificial intelligence startup

selling AI software for investment bankers

and Wall Street analysts at a valuation

of up to $350 million.

You know what investment bankers need?

They need that, what was it, OptiFi.

That would be the big opportunity in Wall Street.

If you wanna sell into Wall Street banks,

go to the OptiFi guys and say,

hey, we're gonna put cameras in every cubicle

in your investment bank,

make sure these guys are really working 80 hours a week.

They always talk such a big game,

oh, investment bankers work 100 hours a week.

Oh, show me the data.

Show me the data.

I don't know if I buy it. It could all just be a LARP. I want to see it.

Anyway Coastal is already in. Thrive is a big open AI investor. They're

participating in the new round. Styling itself as Wall Street's first AI analyst.

Rogo aims to shorten the time that investment corporate bankers spend on

the grunt work of research and preparing client materials. Love that. Three year old startup.

Yeah, this feels like a better attack vector for the big slide deck problem, right? A lot

of white collar work is making slide decks. A lot of time and energy goes into it, but

the challenge of making decks is not generating pretty pages. It's what is the content that goes into it.

Yep.

You're going through all this data, you're creating models,

you're creating charts, graphs, et cetera.

And it seems so obvious in the context of Harvey.

I'm surprised that we haven't seen anyone do this before,

because with Harvey, obviously, it's a generative AI startup,

customizes AI models using legal data, such as case histories to save lawyers prep time.

Harvey's ARR topped 50 million in December.

We've heard that it's a pretty expensive product,

but they're selling to law firms and saves them a lot of

times, it's probably worth it.

And Harvey is now at a $2.7 billion valuation,

and it makes so much sense that there would be a Harvey

for investment banking.

And one of the big things is,

if you're an investment banker or a lawyer,

you you're going to use chat GPT deep research if you could, but oftentimes you cannot

put client materials into open eyes models that they'll train on because all of a sudden you have some secret

information that's meant to be very private and

they get trained on it and then in the next version open AI

GPT 4.8 comes out and you ask it like how much does this person make it this company and it's just like here

We go or like, you know, what's the what's the intellectual property behind X Y and Z?

It's like oh, yeah, like the lawyer who was working on that intellectual property

They uploaded it all and we trained on it by accident. It wouldn't even be open AI trying to do that

They just wouldn't they would just be yeah, it's in the it's in the feed. We got the data. Let's just trained on it by accident. It wouldn't even be OpenAI trying to do that. They just wouldn't, they would just be, oh, it's in the feed, we got the data,

let's just train on it.

And so, makes a ton of sense that you would run a,

like a sequestered LLM that could be adapted

to all the data that the bank has,

but then also not leak data from one client to another.

What were you gonna say?

I'm curious to know what their actual policy is around that.

They obviously wanna use the data that they ingest

to improve the product.

But are they using it to inform outputs to other users?

Like actual factual outputs?

Yeah, I don't know. I mean, I think, I don. Yeah. I don't know.

I mean, I think I don't know.

I think Harvey is not doing any of that.

That's like the risk.

That's the risk.

That's the risk.

But we don't know if OpenAI is actually doing that.

I mean, in the long term, you could

imagine a kind of data sanitization and anonymization

strategy that takes in private data

and still allows it to improve the model.

But it's probably very, very tricky

because if any of that data leaks in and you ask it,

it's very easy to figure out what's happening

with these models.

For a long time, if you went to OpenAI's Whisper

and you just had it record some audio and

then you didn't say anything and then you clicked, okay, like transcribe that, it would

say, thanks for watching, please subscribe.

And it's like, okay, that's clearly YouTube data.

And so you could imagine this data leaking out.

And already, I mean, I'm sure OpenAI is trying really, really hard not to let personal information

leak into the training data because I noticed that OpenAI has a series of personalization

features where it tries to learn about you, but I will often lie to it.

Can you imagine how bad it would be for an investment bank if you were able to query

like about ask open AI about something and it just pulls up,

oh yeah, this company like tried to sell itself

three or four different times.

They ran all these different processes.

Goldman was lead left in the deal.

They bailed. They couldn't make anything happen.

Here's the name of the banker that was looking at it.

Internally, they said it wasn't that good,

but they tried to shell it on somebody.

Yeah, it'd be a disaster.

So obviously a clear need,

and a lot of people are swarming in here,

such as Hebia, which we talked to, George Savolka,

Model ML, pro sites going after the task

typically handled by overworked analysts and junior bankers,

and several banks, such as Citigroup and Bank of America say

they're also developing AI tools internally for similar purposes. For

Thrive Capital, which made big headlines for bets on OpenAI and Stripe at

relatively high valuations, the rogo deal shows the firm also wants to make

investments in younger AI companies. The New York Investment firm is also in talks

to invest in the newest financing for popular coding assistant cursor. We heard about this earlier at I think a 10 billion valuation and so

Kushner's all over the place. He's going down to the 40 million dollar round. He'll do a 1 billion dollar round

He's an absolute dog size lord, but let's ring the size gong for

Kushner and well if you want to invest in companies that Kushner invested in 10 years ago, why not

check out Public.com?

Public.com, baby.

Investing for those who take it seriously.

They got multi-ass.

Josh has a knack for investing in stuff before it ends up IPO-ing, which is a pretty good

business.

Yeah, pretty good business.

I think he described it as buy low, sell high.

Yeah. I think that's the strategy like buy low, sell high. Yeah.

I think that's the strategy over there.

Or just hold forever.

Yeah.

Hold to three T's.

Yeah, let's do it.

Well, they got multi-asset investing,

industry leading yields, they're trusted by millions.

Head over to public.com to get started.

Thank you to Public for supporting the show.

We love you guys.

Thank you to Public.

Anyway, speaking of Mag-7, big tech stocks,

big market movers, Apple, Meta, Google,

they're buying remote control to robotic arms.

We talked about this briefly on a previous show,

the arm farm at Google, I love this one.

Wait, by the way, I didn't realize this article

is written by someone with the information name Rocket.

Cool, I like that name.

Rocket Drew. Being called Rocket.

That's a great name.

And then writing about deep tech is just.

Amazing, great nominative determinism.

Perfect.

Your future is bright for Rocket Dru

over at the information.

They write, during Nvidia's conference for developers,

last week Jensen Wong showed off a software

that creates computer simulations of robots.

Those simulations aim to teach robots

how to perform tasks from washing dishes to picking up household objects but some robot

makers I spoke to say it's better to train robots to do such tasks by having

a person control them remotely also known as teleoperation and this has been

like the most popular topic but also controversial oh Elon did the the

optimist event and they were tele-operated is this like maybe tele-operation is actually the path to

Robotic AGI and so it's good to be on that path, but then everyone else

Kind of is like wait what it's tele-operation

I mean we could put each of us put an optimus in each other's houses and instantly teleport into it

I could come over you're sleeping

We got breaking news.

We got breaking news.

We got breaking news.

That'd be great.

Hey, not too distant future.

I hope so.

In a sign of growing interest in tele-operations,

Scale AI is considering jumping into that market

according to people who have spoken to the company staff.

I was talking to Alex Wang about this

a couple years ago actually.

He had a great interview on Invest Like the Best

and he talked about the data wall in robotics,

the fact that yes, there's a trillion tokens of words

on Reddit and the internet broadly

that are very easy to crawl

and that's why the LLMs have advanced so quickly.

That data set does not exist anywhere for human motion data.

Well, I'll go out and say, I have content of me

kick flipping, surfing, snowboarding,

bunch of cool stuff.

But were you wearing a mocap suit?

Because we gotta know where the joints were going.

The video's not enough.

Now, they can do translation from video.

Put me in a suit.

I would like to train T optimist on kickflip.

I think that actually might be the future,

and that might be what scale's going to do.

Scale might have an army of,

we talked about this with Mercore today.

You're gonna get paid to serve.

Yeah, no.

Right now, knowledge workers globally

can just train models by writing code,

answering questions.

I mean, that's the Mercore thing.

It's like you are gonna hire people

to answer math questions. The greatest, that's the Merckor thing. It's like you are going to hire people to answer math questions.

The greatest opportunity of the next five years

is to wear the suit and just do awesome stuff.

Just do sick extreme sports in a mo-cap suit.

Why not?

Can you imagine you're out snowboarding in this suit

and you just have terrible, like you are flailing on some jump.

You're like, all right, we gotta like cut that out.

Like, I'm sorry.

Pull that from the training data.

It's real, like it should be in the data,

but like at the same time, I don't wanna, you know,

I don't wanna set a poor example.

Exactly, you gotta call all those data points.

Remember, remember I talked about too,

I wanna have, you know, I think that the real benchmark

that matters for all humanoids

is the ability to do extreme activities.

I agree.

So cliff jumping, a robot should be able to-

900, backflip, barrel roll, deadlift.

All the tricks.

To 1,000 pounds.

Yeah, when a robot can just be in 1,000 pounds.

Clean and jerk for sure.

Yeah.

These are important evals.

Scale has an army of human contractors who create data to train AI and evaluate the performance

of AI models in difficult tasks.

The company has discussed using that workforce to handle teleoperation for training robots.

And I think we were talking to a company that was doing teleoperation for those small delivery

robots which have been getting more and more popular.

And I've long said, I mean, George Hotz had a take that Google Waymo was overly teleoperated

in the sense that there was a human in the loop too much, basically, a human in the loop

overseeing one or four or eight or 16 Waymos at a time. And basically, there's always a

human behind the scenes and Waymo that's ready to like hop in if there's a

problem. I don't really have a problem with that. Like, let's see how the

economics pays like pencil out. If if there needs to be a human in the loop for

most of these robotic things, and that's helped and that helps us develop the

training data to get to really, really autonomous systems over time. I'm fine with it

I'm not a I'm not a I'm not like an AI purist in that regard

and so

Large firms such as Tesla open AI meta and Google and Apple are trying to develop hardware or software for humanoid or home robots

There's also a bunch of startups doing this stuff

Sensei is another rival says it wants to be scale AI for robotics training data

and aims to distribute cheap tele-operated devices

to a network of human data collectors.

This is your idea.

Who will perform tasks such as folding laundry

on behalf of robot developers.

Yeah, we need Sensei for extreme sports.

We need scale AI for kickflips.

Yep, I like it.

Scale AI is up at 14 billion valuation.

The kickflip is the final male benchmark.

I think it is.

You can be in the thousand pound club.

But if you can't kick flip.

What are you doing?

Well, dunking.

I would say you handle the kick flips,

I'll handle the dunking.

Okay, yeah, together we make a good team.

But until I see an optimist or a figure robotic robot dunking,

I still got a job.

Let's see.

Yeah, figure train their new they trained

their robots on Joe Biden yeah and Joe Biden I saw and they were saying today

this is the last this is the last time because they're gonna train on someone

athletic next yeah that's interesting yeah anyway in the relative world in the

relatively small world of robotics teleoperation equipment is hot Tros Trocen Robotics, a long-time seller of robot parts

in recent years, began selling Aloha,

a teleoperated device with four arms

that allows a human operator to use two arms

to control the other two.

Interesting.

The devices sensors collect information while the arms move

and the robot is trained to repeat the motions.

There are multiple versions of Aloha,

including stationary and mobile,

the latter of which was designed at Stanford.

Trosyn is based in Downers Grove, Illinois.

Last year sold more than 100 stationary and mobile Aloha devices together, which have

a sticker price of more than 3.3 million, from only a handful of sales.

And so they're doing well.

There's also robotics.

Some roboticists are collecting tele-op data using more rudimentary gear including some game controllers

Dexterity which develops robots that pick and pack pick and stack packages and trucks and other areas

But Xbox controllers and connected them to robots

Very cool human staff use the controllers to direct its machines to stack boxes

And so maybe in the future, you'll just be downloading the latest Xbox game from scale AI and just

Tele-operating for you know points in the game basically the golden age

Is going to involve people moving to very inexpensive countries and getting paid to do fun stuff all the time

there was a there was a performance artist named writer rips who

when VR was getting hot, built a

VR simulation of what it was like to be in a pick and pack facility in an Amazon workplace.

It was very bizarre.

And so you would have to pick up the box.

And it was the only, the game was just work.

It was just work.

That was it.

It was very interesting.

It was very like, he's like a thought-provoking.

How many DAUs did he have?

I mean, it was something that was shown at fine art museums, basically. He's very like, he's like thought provoking. How many DAUs did he have? I mean, it was like something that was shown at like fine art museums, basically.

He's like, he's an artist essentially.

But it's like thought provoking work.

He's a wild guy, but he's a character.

Anyway, you know what I think the final eval will be

for these humanoid robotics, these robotic arms?

I know what you're thinking.

I think it'd be flexing with a nice watch

on the robotic arms wrist, of course.

We gotta get robotic.

You know these robots aren't approaching true AGI.

Until they're rocking an aquanaut.

Yeah, exactly.

Yeah, I mean, honestly, if you're spending,

what is this, $3 million on a robotic arm,

throw up a tech on there.

Why not?

It's an easy way to stand out.

At least put a Daytona on the thing.

It's an easy way to signal to buyers that you have shared

value.

Exactly.

Hey, yeah.

This robot, it's got some class.

It's not just like automating, not just stealing jobs.

It's also raising the aesthetic floor in your office

I love it

So where should they go to buy watches for the robotic arms Jordy?

They should go to get bezel calm download the bezel app they should

Build that your bezel should integrate with scale. And so you can just, you're doing the training data

and then you're immediately cashing out for watches.

I volunteer to provide the training data

for buying watches on Bezel for Scale AI.

And yeah, training, okay, how do you properly

check the time on your watch?

I don't know if a robotic arm could do that effectively.

That's right.

And so we need training data for that.

And of course, we're gonna head over to getbezel.com,

shop over 23,500 luxury watches,

fully authenticated in-house by Bezel's team of experts.

Fantastic.

Anyway, we got five minutes.

We got some breaking news.

Taylor Lorenz just commented on Alex Conrad's post,

announcing that he's coming on TVPN saying,

powerful collab, and she hit it with a repost.

So shout out to tech adjacent journalist,

Taylor Lorenz, the one and only.

Separately, Shkreli is saying that CoreWeave

is 5X oversubscribed and will IPO.

He was going back and forth.

So we're having Tane on the show from Wing.

He does a lot of deep dives on S1s and I asked him to prepare something for CoreWeave, which

I think will be very interesting.

But it sounds like we have Christian Garrett in the Temple of Technology.

Welcome to the show, Christian.

There he is. How you doing? Good to see doing guys? I'm good. I'm good.

How's it going, John? It's great. Good. I'm happy. It's a beautiful day.

Where are you calling him from? I'm in San Francisco, so I am,

I'm holding it down and depending who you ask,

this is the future or this is Detroit.

So I'm enjoying finding out what's going to have it.

Have you checked your signal group chats for?

Reporters yet. Yeah, no, I man I really need to step my signal group chat game up. I could tell you that much

Yeah, yeah, just take a pass at the member list if you see Taylor Lorenz in there, maybe

Create a new chat, you know, you don't need to kick her out. But you know start a new one. Yeah

Yeah, the important conversations elsewhere. Well, thank you for joining.

Can you give a little bit of an overview of who you are, what you do just for the,

just for the folks on the show who might not be familiar?

And then we'll go into some questions.

Yeah. So I'm a partner at one three seven ventures.

We're a growth stage venture capital firm.

And we want to invest in what

we believe are generational category defining companies that can be long compounders and

have defensible, sustainable competitive advantages.

Like every firm, we have a differentiated strategy.

A lot of what we focus on is as a liquidity partner to companies.

We do do growth capital, we do invest in primary rounds.

But we saw a long time ago really up the heels of Facebook

and after spinning out a founders fund,

we saw the opportunity to partner with companies

on the liquidity side as a way to invest in them

and build positions in them.

And that's what we've been doing for a while now

and that was a contrarian bet

that companies are gonna stay private longer

and there would be growing demand for liquidity. it's you know somewhat consensus and and and popular and understood

Yeah, I think Peter was basically banging the table saying never go public and now you have Elon kind of saying the same thing

Hey, Tesla's kind of rough go obviously did very well

But got kind of you know beat up in the courts and whatnot

And so it's great to see that it's at least an option for those founder led companies to stay private longer.

And thank you for your service to the capital markets.

It's fantastic.

You got a question, Jordan?

Yeah, I'm curious.

There's been a meme for a very long time that,

oh yeah, I'm an early investor in SpaceX,

but like maybe there's like a bunch of SPVs separating you

and like the actual like actual, you know, certificate, right?

They certainly don't have the certificate.

How do you think that average investor has done

over the, that's like investing into these sort of like,

which is not what you guys are doing,

but when these sort of power law companies

end up just crushing and growing tremendously,

does it matter that you're stacked in layers and layers of fees?

Do you get smoked?

Can you come out alive?

What's been?

Yeah, well, let me, I'll take a step back too

and kind of make a broader point.

I will say it's funny you picked SpaceX.

I do have a rocket engine right beside me.

Oh, nice.

Oh, yes.

We do have a SpaceX rocket engine here in the office.

That's fantastic.

Amazing. So, okay, so let's take a step engine here in the office. That's fantastic. Amazing.

So, let's take a step back.

I'd say for the last two decades, companies have trended towards staying private longer

and longer, like we just talked about.

And in order to do that, companies need growth capital and they also need liquidity capital.

And the secondary market is just a tool for private tech companies that works just like

the public markets in that it just provides liquidity to existing shareholders.

There are two distinct segments of that market, which is what you're hitting at.

One segment's done in partnership with companies, which is where we at 127 Ventures focus on,

and another segment operates outside of that.

You don't want to operate outside of that.

We've been long-time Android investors, and they have tweeted a ton about fake allocations

in their primary rounds being marketed to investors. They have tweeted a ton about fake allocations in their primary rounds being marketed to investors. I will say what you're hitting on is mainly just the proxy for demand.

Investors want to invest in great companies, regardless of how. As demand grows, investors

look for supply, and there's only so much supply for primary, which I can talk a little

about why that is. Secondary is another way to access a company's equity.

And so people will do things to your point on investing in various SPVs or whatever it

is as a way to access.

And I think some of that is good and blessed by the company.

It's just another vehicle avenue to put capital in these businesses.

And then a lot of that operates outside of that and is kind of a black hole and maybe

not the best place to be in because you one don't collaborate with

the company and then two, you don't have access to information. Right. And so, um, and the

third is potentially like Andrew was tweeting about is there could be fraud as well.

Sure. Uh, can you talk a little bit about why, like how companies think about doing

these tender offers, when they do them, when's the right time and how, how do they go over

like culturally, obviously there's some incentive and employee led, when's the right time, and how do they go over, like, culturally, obviously,

there's some incentive and employee,

let's just like reward the employees,

but what other considerations go into a successful tender?

Yeah, so the tenders and just the broader market

we're talking about has grown dramatically over the years.

And one of the interesting things is like,

a lot of these companies have made the transition

to being cash flow positive in the private markets,

which means that more shares are actually bought

in secondary than primary through things like tenders,

over the life cycle of the business.

Databricks just did that massive round

to convert and pay the tax bill for a lot of the RSUs.

SpaceX has raised $10 billion in primary

over its 23 years of being around

the company. They've been running two tenders annually that total more than a billion and

a half dollars a year for a long time. And so, I think a lot of companies are falling

in SpaceX's footsteps particularly and building liquidity programs like theirs, Stripe, mention

Databricks, Plight and Tuition, OpenAI, Androel, a lot of them.

What hasn't changed is that it matters

who your investors are.

So great investors, like they may not make your business,

but terrible investors will definitely ruin it.

This is why the best companies want to control

their cap table as always.

And you'll work with investors like us

on implementing the liquidity strategy as they scale.

And more companies as they stay private longer,

as they've scaled, even as they hit cash flow positive,

tenders have been a way for them to offer liquidity

and kind of postpone going public.

And it's a way to align incentives.

It's a way for recruiting and retention.

Like you mentioned, right?

If you're recruiting against publicly traded companies,

if you're recruiting software engineers

against Google and Meta,

or you're recruiting researchers engineers against Google and Meta, or you're

recruiting researchers from Nvidia or Google, you want to be able to offer not just a compelling

package and upside, but being able to offer liquidity also helps bake into folks' comp decisions.

You have people that have structurally have to run these tenders based on their RSUs,

like Rebex is on the single-trick RSUs, and so they structurally have to run these tenders based on their RSUs, like X is on the single trigger RSUs,

and so they structurally have to run them

for their employees' tax bills.

There's a bunch of reasons.

Some people also use them to mark the business up, right?

If you're not raising primary

because you're cash flow positive for years,

then liquidity checks a bunch of other boxes,

but also allows you to continually show progress

in the stock of the business.

So I just think as the capital markets have grown,

as these companies have grown,

the secondary market has obviously grown with it.

And I think a lot of the best companies

have had the privilege of working with their investors,

working with folks like us,

people they want on their cap table

and to grow on their cap table to run these programs

and control and manage liquidity

in a way that's beneficial for the company.

Have you guys looked at any businesses that are basically

building actual basically software

to manage these liquidity programs?

And did you guys ever think about incubating something

there?

Or is every company unique enough

that it should just be done by the investors

and the company's counsel, and it's just all bespoke?

Yeah, I mean, there's like two versions of that.

There's the software to run these programs, which exists.

Right, Carta has great software, right, for running this.

And so I think, you know, that's just back to like

broader cap table software management trend,

which is awesome.

But that's like more of the execution side.

The other side is more of creating a market, right?

And then using software to facilitate more liquidity

and grow liquidity.

And that is basically another version of the same thing

we talked about earlier, right?

Which is like the best companies want to control

their cap table.

The best companies have unlimited demand, right?

And so in that, in that essence,

you don't need a broader market to have random buyers

and sellers to do price discovery, right?

And so I think the best companies generally like to run

their own processes and work with, you know,

their major shareholders and a lot of times, you know,

which includes us and a lot of these companies as well

on kind of running these processes,

very similar to how a primary process would run,

just a different type of transaction and goal.

Yeah, to me, it feels like you guys are

in the financial services business in many ways

when you're creating these sort of programs

and you're an investor as well.

And there's been, there's constantly people that see the opportunity.

They see how big it is.

They try to attack it with sort of software and marketplaces.

And then time and time again, I feel like we see them sort of flop.

And you saw this with Carta basically kind of apparently giving up on their

entire secondary brokerage business at some point.

apparently giving up on their entire secondary brokerage business at some point.

But again, people in venture always see a problem

and an opportunity and wanna like throw software at it.

And sometimes it's basically,

companies like Andrew all saying,

yeah, we wanna work with one three seven ventures

cause they've done an exceptional job

with their relationship with SpaceX.

And we want that kind of partner as well. And that just looks more like traditional financial services

versus a venture business.

Do you give any attention to every once a month,

these sort of lists pops up around heat

around different companies?

And sometimes I see this list and-

Well, they're doing your job for you

because you see a list on Twitter,

you can just go hit the company up, right?

Like, you know, you can just, you know,

you don't have to work that hard.

Usually you see 10 companies and you're like,

all those make sense, one of them-

Except for that one.

Except for that one.

So do you give any weight to these lists

or is it just random?

Where do they actually come from?

Because it doesn't seem like it's put out

by 137 Ventures, which I would trust. To me, it could be a single broker any weight to these lists or where do they actually come from? Because it doesn't seem like it's put out by one three seven

ventures, which I would trust to meet.

To me, it could be a single broker who's just basically

pumping their own.

But yeah, you guys, you guys nailed it.

Yeah, I mean, it's it.

I mean, look, it depends where these lists come from.

A lot of them are noise.

They're not signal of transactions and a lot of those

transactions are uninformed buyers and uninformed sellers.

As an institutional firm, we don't pay attention to them and the best companies don't either.

It would be amazing if the job was so simple as to look at a list and press a button and

buy but unfortunately, there's a lot more to investing than that.

I think you'll see them either aggregating a bunch of transactions from a platform level, but still brokerage business, or you'll kind of have brokers who are, you

know, sort of trying to create a market and advertise what they may or may not have access

to.

So, yeah, that is in that segment of the market that I think the best companies don't particularly

like, and that you don't want to be in as an investor on the secondary side that we

talked about earlier.

Yeah.

Can you talk a little bit about like, how do secondary shares work their way into the broker system

and how transfer restrictions work a little bit and how those have evolved over time?

Yeah. So on the first part, I mean, it's a broad range, right? I mean, this is, you have employees

that may not be under transfer restrictions. You'll have a lot of employees that may do transactions

on a forward basis.

So they're actually violating transfer restrictions,

but it's a different type of construct.

You have a lot of these two are just SPVs.

So as investors, a lot of firms will

do co-investment vehicles with their LPs.

And then those LPs will want liquidity.

And so you in essence have liquidity into the SPV, which then allows you access to the

underlying company.

So there's just various forms of supply.

As companies grow, there is a lot of avenues where there just is supply.

And some of it is legitimate, some of it's not, but it definitely is.

There's a lot of legitimate supply for sure, right? From employees, or SPVs, et cetera.

The transfer system side actually hits on like

this whole dynamic, right?

And this is, this actually all goes back

to the Facebook days.

So in the 90s and early 2000s, companies only had a right

of first refusal, and that was sufficient

to discourage random buyers.

Facebook was obviously a popular consumer business

and the first to go to tens of billions of dollars

enterprise value in the private markets.

And there wasn't as much money in venture back then.

So the company and the company lost control of its cap table

because the volume of shares that traded was well beyond

what the company or existing investors could purchase.

And so you basically just had a lot of outsiders

being able to buy, right?

Cause there's a ton of demand.

The existing investors weren't able to just use a rofer as a way to buy it and control it.

And so once other venture companies saw this, they implemented basically blanket transfer restrictions.

And that has been the default ever since.

And so you have to understand that the entire benefit being private is that companies can choose who they give information to and allow a cap table.

No founder wants an activist investor.

And if you go your cap table, it's kind of no longer your choice.

And so transfer restrictions have sort of been the default.

Even in the case of Facebook, Yahoo could have potentially built a position or Google

could have built a position in the secondary market and then had rights at some point,

which would be potentially disastrous.

Didn't happen, but you know, that's the risk.

So if there are no transfer restrictions, does that mean like an early employee could just

meet a random VC at the Rosewood and say, hell yeah, I'm sitting on two million dollars of stock

in this company. You want to take it off my hands and they can just do that over a handshake and

some contracts or does it eventually need to bubble up to like the company? How does the

company actually go from their shareholders?

There's still a roper, right? So yeah, and like I said before with the right first few

years, it was enough to discourage this. But then with Facebook, the demand overwhelmed

the ability for the investors to actually execute that right, right? From a capital

perspective. And so

And the roper is just the roper is discouraging because if I'm trying to build a position in a company through the secondary markets

There's no transfer restrictions. I know that I go to an employee. I say hey you have two million dollars

I'm gonna keep running into this problem where we get a handshake deal

I'm gonna buy two million and then the company buys it and then I go to the next employee, right?

And it's just a waste of my time. That's the main structure

or the other

Talk about the companies you invest in, or many of them

you described as having effectively unlimited demand

for the equity.

And right now, we see venture funds that have ballooned,

and they have more capital than ever to deploy.

It used to be these companies would

get to the point where the VCs would be like,

I remain giga long your company.

I just like, I'm fully tapped.

So like, I just got to let it ride.

Now it's less the case.

Sequoia funds three with like 30 mil.

Have you seen, do elbows get sharper

in some of these later rounds?

Where I imagine from an AUM standpoint,

like you guys have ton of AUM, but you're coming to the table with people

that might have 10 times as much AUM and these capital bases

where they can hit up a sovereign and be like, hey, we're

doing an SPV into this one. Do you want to come in?

5 billion.

Yeah. So what's the competitive dynamic in the in the sort of

later stage?

Good question. Um, you know, I think it's a bit I'd say like to your

point 100% as as these companies really scale and demand, you

know, demand obviously follows suit with the performance of the

fundamentals of the business and this and how they've executed on

the story. You you do see obviously a ton of I mean, you

know, SpaceX does a tender and their 10x oversubscribe, right?

That is, you know, billions and billions of dollars of

demand that is unmet.

And the investors, to your point, the venture ecosystem has grown, so there's a ton more

dry powder in the market as well.

But also, I think the size of these tenders and primary rounds does scale a bit, definitely

on the tender side.

So I do think as a company

grows, its secondary market does grow, and the liquidity programs grow in size, so that

helps meet some of the demand. But you 100% run into that. Look, I think at a certain

stage it works, but there's a certain stage where there's more demand for SpaceX or Andoril

than there is supply, and that just is the function of it. And I think

that's where relationships really matter. But even then, they're still a link. So I would say,

I think relationships end up being the biggest driver there for your ability to still,

not just obviously get an allocation, but also try to continue to size up the position and invest

more. And I think being a major shareholder,

being around for a long time,

and having very close relationships,

which is what we focus on, gives you a-

Yeah, it's a likeability.

It's a likeability.

Allocation and venture is like,

often comes down to likeability.

It's like, does the CEO and the management team like you?

If so, cool, we're gonna give you preference.

If not, you know, you might get your prorata,

otherwise, good luck.

Being an SPV promoter is more like being a club promoter

than being a VC or something like that.

I have a more like tips.

Venture is unique because it's a unique asset class given

how important access is.

And access and that dynamic there leads to you you could be a you could end up getting

access to an incredible company and and maybe even still be a schmuck to your point.

However, doing that consistently and over a long time frame, I think is a different story.

Yeah, yeah, totally. How do you advise founders that are kind of reaching the territory where you guys are starting to invest?

I'm going to pull out a number. Let's say they're close to nine figures of air are their real business now.

It's working. They're raising a bigger round that some mix of, you know, liquidity for the team as well as, you know, some some growth capital do and they're worried about kind of like signaling risk around selling secondary.

Right. In the public markets, you see this.

It's like, OK, this CFO is like selling a huge amount of their position.

That's obviously bad. Same thing on the founder's side.

If the founders are selling huge amounts

of secondary, it can be a bear signal.

And we saw the worst of this in 2021 and 2022,

where founders would be selling like $50 million

like pre-product market fit.

And that wasn't common, but how do you advise founders

as they start to get opportunities to get liquidity

and they're sort of worried around,

well, I'd like to be able to like buy a house

and put my kids through college,

but without stressing about college, but without

stressing about it, but I don't want to send the wrong message.

Yeah.

I mean, I think you hit on the reality of obviously there are the obvious extremes,

right?

Which is, you know, the founder selling 90% of his position while still operating the

business.

That's obviously going to raise eyebrows and people are going to protest that.

And the founder, you know, sells $10. also, people probably aren't going to bat an eye.

So what number in between is the magic number depending on stage?

And look, I think one, it's usually driven by life needs.

And so that de facto backs into a dollar number that makes sense.

And so I think in many times the conversation is around de-risking,

about a life need, someone just had a kid,

they're starting a family, they wanna buy a house, right?

And so I would say like, you know,

you're also investing in founders

that you trust and are rational and reasonable.

And usually these conversations are fairly easy

from that perspective.

I don't think there's like a particular dollar amount.

I think one of the things to think about,

whether you're a founder or on the investor side,

is more so you want to think about the two dynamics

around percentage of holdings and then total dollar size.

And those are interesting.

In some sense, if you sold $5 million,

but it's half of your holdings, $5 million

at a certain stage of business is not a lot,

but something like 50% of your position

while still operating may signal something.

And it works both ways, right?

You may be able to sell $100 million, which is a lot,

but it could be 5% of your position, right?

Which generally people would not view as a lot,

and that's the conversation.

So I think it's a bit of like,

it depends on the circumstances and the context,

but for the most part,

founders are pretty rational and reasonable.

And you gotta remember,

most founders are the most bullish

in their company, even more so than the investors.

So the desire to sell is generally pretty tapered

and usually driven by life needs.

Yeah.

Well, thanks for stopping by.

Great to have you on.

Great conversation.

Can we see the rocket again?

Can we see the rocket again?

Yeah, show us the rocket one last time.

Let's see the rocket.

And then we'll get on to the next one.

Here we go.

Oh, that's a beautiful engine.

Let's hear it for the rocket folks. Yeah hear if you end up with a spare rocket we'll throw yes send it over if you got

an extra I need at least three more appearances on the pod I can talk to the

rest of my partners and maybe one piece of adventures will send you a rocket

will fantastic you heard it here first folks it's you. I have a great rest of your day.

Talk to you guys. Talk to you soon. We're going back to back folks.

We got back to seven more guests coming into the temple. I think six.

We got Darsh on from beyond.

He just launched the big screen to the VR headset. We discussed this on Monday,

I believe maybe maybe maybe Friday actually. Yeah.

And it's a very cool VR headset. I think we got him in the temple of technology. on Monday, I believe, maybe Friday, actually.

And it's a very cool VR headset.

I think we got him in the Temple of Technology.

Welcome to the show.

How are you doing?

There he is.

Good.

Thanks for having me.

And congratulations.

Can you give us the breakdown?

What did you launch?

How did it go?

Yep.

So we launched last Thursday.

This is our second generation product, BigScreen Beyond 2.

We launched our first gen about two years ago. This one addresses a lot of the things that people

really wanted out of the next gen one. So for people who probably know this old thing,

this is the Apple vision pro.

Yep. I had one for exactly two weeks.

Yeah, I've got one on my desk. That's where

Well, you're in the industry. So I expected you wouldn't return yours.

It's a beautiful

It's magical. It is

Incredible technology. Yes, and I've got some some spicy takes but

I don't think anyone wants to wear a brick on their face

It's just unless you're skiing or something maybe but even then people don't want to wear brick on their face

So we've been working on this company for about ten years

We raised some capital from Andreessen and true and we set out to build the world's smallest

VR headset. So we think that VR is much more like wearables, much more fashion centric

actually. So it needs to be super comfortable. We're chasing after enthusiasts, not mainstream

mass market. I think we're playing a 30 year game. People are like kind of in it for let's

start a thing, build a whole thing,

like flip it in two years, blah, blah, blah.

Like we're actually playing a long-term game here.

So we built Pixel Beyond 2.

It is the world's smallest VR headset.

This weighs two thirds of your iPhone.

Like an iPhone is heavy compared to this.

And it looks pretty freaking cool.

I think it looks great, yeah.

But congrats on the launch.

Yeah, when you think about playing 30 year games, how do you think about just capital efficiency?

There's the meme that like hardware is really expensive and all these companies like I

Imagine you you run if you're playing this sort of long-term games. You're like, well, we need to be in business for 30 years

We need to be able to have big moments where we sell a lot of products and then

Yeah, we're going through

dark times. I'm sure you've been through both already, but how do you think about durability

of the business given that you're selling hardware, which will just end up, you're going

to have fluctuations in demand.

A couple of things. I'm pretty sure I don't know if they wanted me to say this publicly,

but I'm pretty sure with the single most capital efficient company in our investors' portfolios.

Let's hear it for capital efficiency, folks. Thank you. Hit the gong for, in our investors portfolios, capital efficiency folks, thank you.

The gong for that. It's not typical, but we love some capital efficiency on this

show.

We have raised 17 million from Andreessen and true. And at some point,

I think we had like 10 years of runway. And now, you know,

for a couple of years we've been cashflow positive. We could be, you know,

we could be profitable any minute that we want,

but we put all of our revenue into R&D and the team, and that's it.

Like, zero dollars in acquisition of customers. It's all organic.

Hardware is a lot cheaper than people think. I think Meta is wildly inefficient.

They're spending tens of billions a year to try to accelerate the market.

They're also playing a different game. They're trying to go, they need to get a billion users.

I don't care.

We can make a massive, awesome contribution to the world

by focusing on people who really, really need what we do.

And we can do it efficiently.

Like the number of people at Metta that are doing stuff,

they just throw everything at the wall and at no cost, right?

It doesn't matter.

And frankly, don't tell the shareholders that

it does have a cost

I think the cost is 20 billion

But respect to suck. I love a guy who's chasing his dream. Yeah, but how many yeah, sorry

Go for it. Yeah for us

we're playing a different game because we can stay focused on like real use cases and make a real business out of it and

Like I understand first day of our sales. we did 10 times more than we did for our

first gen. In a couple of weeks, we will have done more sales than we did in 2023

or 2024.

That's amazing. Congrats.

How many how many companies that were high flying, amazing teams came out and

raised more than you like have like you started in 2014, there must have been probably 20 companies that you're like,

you're pretty viable competitor, flashy, raising a lot of money, but then they're just, they

spend it all in two years.

Has that sort of, has that happened like a bunch of times at this point?

There's a bunch of times, like waves of capital and then also hype cycles, right?

There was like the AR wave or there's the NFT crypto wave

or there's this or that.

There's so many waves every year or two.

We've actually just stayed extremely focused.

We're focused on building an excellent VR headset

for consumers, particularly like PC gamers and enthusiasts,

as well as in the past year,

like the businesses that have reached out

that are using our stuff, like NASA is one of our customers.

We have a bunch of customers in aerospace and aviation

Education retail there's like a nuclear energy

Department whose website it looks like they're from the 90s and then buy your stuff. We have no idea what they're doing with it, but

I want to ask about so I I'm kind of like a VR enthusiast prosumer level maybe I've had a number of headsets I've built custom PCs with Nvidia graphics cards to wire them up had the first Oculus and then like the next seven of them or something

they've always kind of wound up collecting dust can you walk me through

what would you recommend just for the first like magical big screen beyond

experience what what's like the basic hardware I should get should I get a PC

should I you know what's the ecosystem look like

to knock it out of the park? What game or what experience am I playing? It really depends on what

floats your boat. So I'd suggest get a good PC. If you're going to build one, build one on computers.

That's all I do. Love it. Great. Do that if that flows your boat. like buy like a good NZ XT PC like a RTX 4080 or 49 get whatever you can afford

Buy the beyond 2 and then it really depends on what you like like racing sims are in

In this just the feeling of like going down like the North life on a car like you can just you cannot get an experience

Like this in real world because you will probably

You cannot get an experience like this in real world because you will probably kill yourself. We're getting a new studio. Yeah, we'll consult with you and

we're going to get the full rig. Yeah, it'll be great.

Flightsim is another one. I've literally flown a 737 out of LAX at night.

Do you need a good last one? No, I think so. Here's a challenge for you.

Make a game that's basically... I'm sure somebody's already made this game,

but you know how every guy thinks they can land at 737 if they were asked to right? Yeah, like that's the challenge

It's like a big screen 737 challenge and it's like you get dropped into a plane engine down and you gotta land it

This is one of the craziest stories

The first time I ever went ski shooting shot like shotgun shooting

I'd never shot a gun before in my life and we were competing and I beat everyone and

everyone was like, is this just beginner's luck?

And I think the reason was that I'd been playing VR shooting games for like a year straight.

I've been playing Robo Recall on the Oculus and I was like, this is second nature to me.

So I really think the VR training thing is real.

One of the use cases that I really enjoyed with the Apple Vision Pro while I did have

it was just sitting there and watching movies in bed at night.

How close are we to having just like a puck?

Like I'm almost thinking like a little Mac mini

that I just link under my bed

that I can just kind of plug this into

because I know it's not fully standalone,

but the benefit is that it's not gonna be heavy on my face.

Is there a way that I could kind of get

that level of experience with the big screen beyond too?

Yeah, so the company is named big screen for a reason. We actually started building hardware

because we wanted, we made software for a long time and we hit limitations. Our software is still

there on the MetaQuest and stuff like that. I've got like, I don't know, six, seven million users

in VR. We actually have a very sizable software platform. But the hardware just was such a big limiting factor

for the past five years.

We couldn't achieve the vision we wanted to under the platform

that was given to us, so we had to go build it ourselves.

And it turns out other people wanted it too

for all these other use cases in gaming or in enterprise use

cases as well.

So we want to build hardware that you can actually

use for movie watching.

But the problem is, I could go right now, turn on my TV and watch Netflix in 4K HDR OLED TV in 10 seconds.

It's pretty good.

D-Guard is to get to that level.

And I'd say we're halfway there.

We're getting closer and we had to build incredible hardware for it.

We're building the software for it.

And at some point our path to going mainstream is basically Metis

Path has been like $300 headset, there's something like 20

million of them. It's doing really great with kids. Our

path, I don't think it's actually, it's not about price,

it's about price to utility. So we want to deliver you like a

two or $3,000 incredible home movie theater system. And you

can play games with it, you can do all this other stuff with it too,

but it's not a price.

It's really, Apple vision pro is $3,000,

but I'm not gonna wear this for,

actually the battery life limitations,

the weight and the ergonomics, it's not right.

It's not the right factor.

What is Apple doing with VR?

Cause I've posted a few times, I was like,

Apple's like, they're sort of giving up on it.

Like you can tell they don't have real conviction.

They're just like, they're in this highly commercial phase where they're just

going to extract as much value out of the existing technology that they have.

And that's, you know, can be good for business, but I posted a couple of

times and people get angry.

They're not quitting VR.

They're not.

But what are they actually doing in your view?

And are you the next CEO of Apple?

I think Apple, I'm actually surprised

that Vision Pro came out.

They've been doing the work for a long time,

but I wouldn't have put it out, not this way.

I mean, it's setting the wrong expectations,

creating weird hype cycle.

This is not the next iPhone,

but I think Apple is patient and is gonna play a 10 20 year

Game as well. They don't need this to become an overnight success. It's fine

Who cares what the markets say like they've got the cash for it

They can they can do it and they're also doing it in a relatively cash efficient way compared to meta

So they're playing a long-term game. I think they'll stick with it

I think it's in the hands of developers, but I think the problem is there isn't really anyone saying no in my opinion

I don't know how Apple actually runs anything, but in my opinion

No, people aren't saying no enough like

How do you how do you think about focus generally a big screen right? I'm sure people are saying hey build this for

factories build this for

military build it, you know, and I'm sure you've had, hey, build this for factories, build this for the military, build it, you know,

and I'm sure you've had to, in order to be capital efficient

and create great products, you've had to say no a bunch.

Do you have ambitions outside of entertainment

in the long run or are you, is this an extent?

Absolutely.

Yeah.

The nice thing about what we do is that we're laser focused

on a set of problems that happens

to cater to the needs of a bunch of people.

So the enterprises that are coming to us, they're using VR for real work for many hours

a day versus the cycle.

They all have Apple Vision Pro and Quest and all that.

They can afford all the devices.

They've tried them, but you'll use it for an hour.

You achieve your thing and you got to go charge it for an hour. That doesn work for most use cases think of this as Apple and matter trying to build the next smartphone

Meanwhile, we're trying to build the next workstation the next

Actually canceled their workstation focused VR thing I want to I want to ask one more question

On the Apple vision Pro. Can you give me like your pros and cons? Like what did they get right?

I feel like the the external battery and puck was really controversial, but some people say that's really great

What's your take on Apple vision Pro? I

Think they

Established that this industry is really not going any like it's not gonna go away

It's this is gonna be here spatial computing is gonna be a thing

It might take a long time, but it's going to happen.

Apple and Meta are at it.

They're going to go push it.

Uh, that's the best thing that they've done here is, is they've made the world

really understand what is VR or spatial computing and it's going to happen.

What they're getting wrong is comfort and ergonomics matters a lot more.

People are trying to build the next iPhone, but again, no one wants to run

iPhone on their face either.

There's literally a MacBook Pro inside of this thing.

I don't want to wear a MacBook Pro.

Yeah, makes sense.

Yeah, that makes sense.

Uh, broad applications of spatial computing in the military.

Andrew was in the news with winning the IVAS program.

Is the technology ready?

Is it just about getting the product right?

And again, I imagine that's sort of a 10, 20 year kind of vision as well.

But it's not where you guys are building to my knowledge.

But yeah, what's your take on that?

Was it Microsoft just had a good shot but didn't have the sort of leadership to deliver on it?

Or was the technology just truly never ready for what they

were being asked to do? I think that came out of an older generation, the 2016 era hype cycle where

a lot of products were coming out that were telling a story that they really couldn't meet.

So HoloLens, Magic Leap, etc. were touting this vision of like, oh, we're gonna be able to do all these things.

And what really matters in a nascent emerging technology

is yeah, but what can you do with it today?

Like be honest that when you come out of the gate,

what is this gonna be amazing at right now?

Like, so for us, racing simulators, gaming, entertainment,

like really great things that people can do

right now today with this.

And we're honest about that.

Too many companies back in that first generation hype cycle,

yet like they were putting out a product

that the military could not, it didn't work at all.

And it was billions of dollars for that.

So now you're having people come out like Andrew

that are putting out devices that should be able

to actually deliver with the promise

of current generation technology.

What can you actually do with it?

That's great.

Well, thanks so much for coming on.

We gotta have you back to talk about VR

every time there's more news.

Yeah, you haven't opted in,

but you're our official VR correspondent.

There's so much to talk about here.

It's such a fascinating technology.

I think people have kind of written it off

from time to time,

but I'm continuing to be fascinated by it.

There's so many cool developments.

I'm really happy for you and the team too.

Congratulations.

I'm sure the last week has been massively vindicating

and you guys deserve it.

11 years in, here's to the next 11.

And look forward to the next conversation.

An overnight success really.

Yeah.

Have a good one.

Later.

Talk to you soon.

Thanks.

Well, coming up next, we got Alex Conrad.

But we got some breaking news.

Ramp has partnered with FP Journe.

Did you see this?

They're having a Padel Tournament in Miami.

And the partners are Ramp and FP Journe.

You'll love to see it, folks.

Love to see it.

FP Journe, of course, maker of fine watches

owned by none other than Mark Zuckerberg has some FP Journes.

Francois Paul Journe, one of the greatest watchmakers in history, still alive, still cooking, and he's using R.A.M.P. baby.

He's on.

Yeah, I don't know if this was supposed to be breaking news, but it is now.

It's pretty awesome.

If he texts us, I'm going to talk about it.

It's amazing.

It's a public website, I think.

I mean, maybe this is a public website. Yeah. I think. I mean, maybe this is maybe I think this is a public website. Yeah. I think I think it's a public website. Extremely tasteful. We

will share this. I'm very excited about this. If you like Padel, we will. We'll share the link at

some point and you can go ours. We fantastic. Anyway, we got Alex Conrad coming into the temple

of technology. Welcome to the show. Congratulations. Big day. Big day. Hit the gong for upstarts.

Let us know what you're announcing, what you're doing. Break it down. Yeah. Big day. Let us know. Hit the gong for UpStarts.

Let us know what you're announcing,

what you're doing.

Break it down.

Yeah, thank you guys.

I'm so excited to announce my new startup today

called UpStarts Media.

UpStarts Media is a new tech media publication

focus on the startup ecosystem.

Fantastic.

What's the angle?

What are you doing differently?

What are you leveraging and will there be a list

of the best and more importantly the worst venture?

capitalists dropping soon I

Know I know that I have a customer in you for that for sure

Yeah, yeah, I'll think about that, you know, I actually did 25 audience calls ahead of time

And I should have I should have asked that specific question. Should I launch an anti-mitos list?

But yeah for your your audience who don't know me, I spent 12 years at Forbes covering venture capital

and startups. I really lived in that world, you know, wrote a bunch of cover stories about folks

like Melanie Perkins at Canva, the Collison brothers at Stripe. I wrote one about a soft

rap report at Wiz, which has been in the news a lot. You know, really enjoyed writing about startups

and the VCs who fund them. And I felt like we were in a moment where so much traditional tech media

coverage is focused on big tech politics. You know, we have tech people in the White House,

big policy debates, not so much on sort of the startups that I really love writing about. You

know, I just heard from so many people that it was just hard to kind of get those founder journeys,

you know, startup storytelling out there right now.

And so I'm hoping to do my small part to just tell those stories.

How do you think about the different products that are offered in the media ecosystem?

I mean, most people just think like it's a news article, but once you dive in, you realize

like there's investigative journalism, there's breaking news, there's profiles, there's op-eds, there's editorial, there's all this different stuff.

How do you think about the landscape and what interests you the most?

Yeah, well, first off, you know, these tech bros showed up and they just completely created

a seismic event for us in media.

No, but seriously, like jokes aside, you know, I think you guys and a lot of these new brands

that have been the most interesting in tech journalism and media

right now have kind of come from these adjacent spaces. They haven't been

traditional journalists. We have seen those some people go independent and try

to kind of get more direct. You know, we keep hearing go direct, you know, from

certain founders and PR folks. And I think that's great for certain people.

But my hope is that there's still room for curated storytelling from journalists like me

who can help, especially those founders

who maybe don't have the platform to go direct,

and also can just maybe connect the dots

in ways that you wouldn't get

from some of these awesome podcasts and shows like your own.

I mean, I really do agree with you.

We were talking about to Lulu about this yesterday,

just the idea of like, yes, you should go direct

and post your own news,

but then you should also talk and post your own news,

but then you should also talk to new media like you and us.

And then you should also talk to the Wall Street Journal

if they come calling.

And it's really like an ensemble strategy

to build this like cinematic universe around you

and what you're doing if it's important.

Yeah, how do you think about, you know, funny timing.

So we talked about this last week

About tech crunch

selling

It was unclear what they were gonna do. I think tech crunch had sort of created this

The thing they did well was like make people's parents proud, right?

It was like you wanted to get into tech crunch

It was just sort of like this moment and every founders journey journey. You go there to announce a round or for product launch or whatever,

and they sell to private equity, which people were like, oh, great.

Like private equity is just going to come in and, you know, I don't know.

You know, nobody knew what they were doing.

Then the first TechCrunch headline I see is this like hit, you know,

drive by hit piece on 11X, which whether or not it's fair,

it's like TechCrunch is in a very

weird position around, they're I guess trying to do investigative journalism, but then they

still want to be the place that maybe you launch your startup.

Are you trying to pick a lane in saying like, we are pro founder, we are pro tech, we know

this is hard, but we want to like, you know, tell your story in an authentic way that makes

like, are you looking to really like develop trust with these founders and cover them across

their entire career?

Is, you know, what is that?

Like, I'm trying to kind of hone in on, on your specific angle, because I think

the temptation is, you know, uh, somebody starts out writing tech positive and

then eventually they get some crazy scoop and they're like, Oh, this is going

to get so many, this is going to get so many subscribers. Yeah. I'm just going

to publish this funds returns. But I'm curious. Yeah, I hear you. I have like three different

responses for that, but I can try to keep them short. It's really important, important

debate. I think, you know,, I would say our ideology is that

Upstarts was founded on the belief

that startups are at their best

when they punch above their weight,

challenge the status quo,

try to improve the world in some way.

And I think at that core,

I believe that technology is great for the planet,

great for our daily lives.

And I wanna write about that.

I think at the same time,

I am gonna be a journalist,

I am gonna be independent, so I'm not a cheerleader, you know, and just because a lot of my, you

know, Midas VC, you know, pals might be subscribing today, doesn't mean I'm going to suddenly

write about their portfolio company or something like that. You know, I want to keep a really

impartial and fair view. But that's really what I tried to build in the last 15 years

writing about startups was that sense of trust that you can expect me to be fair

to have sort of the good of the ecosystem at heart. So if I do something that doesn't feel super comfortable, I'd say that's actually a good thing because you can get that from an amazing VC

podcast or you can get a beautiful marketing video. I might ask questions that push you a little bit,

but I am in the ecosystem. I do consider myself a founder of a startup here and I have that empathy that I'm going to be only punching up really carefully.

I'm not going to be punching down.

You know, I never want to get out of bed and be like, what startup am I messing

with today?

No gawker 2.0, but, uh, uh, I want to talk about like the instantiation of the

work that you do.

Uh, obviously you're a writer first and foremost, right.

And most people experience your work through Forbes.com essentially

But have you thought about where that lives? Is it are you targeting the email inbox? Will there be a printed version?

I'd love a coffee table book of the conrad list maybe this year. I think that would sell really well

I think every single vc firm would probably pay a thousand dollars for the for the conrad

Printed coffee table book sell a lot of those, uh, are we going to get videos,

podcasts? What are you thinking?

Yeah. So it's a little crazy because I am bootstrapping this business at first to

kind of control my outcomes and test the product market fit.

But I kind of want to do everything you said. I mean,

maybe not the coffee table book just yet. That could be a year and two goal,

but I'm going to be launching a live video series of monthly interviews, very different

from what you guys do, but just a quick fun interview with the CEO next week.

I'm doing that like my newsletter over Substack, who have been a great partner.

So I'm working closely with them and going to be publishing twice a week.

I also got a shout out, you know, and this might be controversial on this show, but I

am going to be working with partners to make sure that one edition of my newsletter is

free each week.

I want to be proving this can be a sustainable business, but also inclusive to folks who

may be our early career students, you know, founders who are cutting their burn and they

want to get high quality news, but they don't want to pay yet.

And so I actually have a launch partner in Brex.

Oh, okay.

Brex is my launch partner.

But I'm always happy to work with others down the road.

But yeah, I mean, that's basically

the way I'm thinking about this is multiple streams,

a newsletter.

I'd love to do a podcast eventually,

but I'm going to be building in public.

I'm going to be screwing up a lot.

I think that'll be, that'll be authentic with this audience.

You know, you guys, You guys will see that.

Awesome, yeah, it's great.

What's the future of the Forbes brand?

It's been an interesting spot.

I'm saying this, you're not saying or confirming this,

but I know they've been like on the market

trying to sell themselves for a long time.

They sold off a bunch of random assets.

Austin Russell was circling.

Forbes book publishing is not really tied

to the parent company anymore.

You know, it's like very unclear.

Like it was an iconic media property.

You tried to keep it alive.

And you know, you.

And certainly more brand cache than TechCrunch, I think.

Like the Forbes brand still has a lot of.

Yeah, but it's been diluted over time.

And part of, you know, if you had stayed and said, I'm going to recommit the next decade and sort of bring it back. I'm sure there's a variety of factors that that didn't allow for that. But what happens with Forbes? I know you probably can't. Maybe you can give your most sort of positive perspective on it.

positive perspective on it. Upstarts is acquiring Forbes in 2026. Scoop, scoop. But to answer Jordy a little more seriously, you know, I started covering startups in 2010. You know,

TechCrunch was a giant. VentureBeat was a giant. You know, Forbes, the website was still

very siloed. So it was Fortune. It's like media has changed a ton in the past decade

plus. I think like people forget that the Midas list was actually started in 2000.

So it way predated off to and it will outlive us all whether he sees like that

or not.

Yeah. Yeah, that's great.

That makes sense.

What do you think the.

What's the future of Substack?

They went through this kind of, you know, period of massive hype.

And then

there was a period where every media platform was attacking them. And then it seems like

they've come out of it. And now people are deciding to go on and build real businesses

from day one on the platform. What's your take on? Are they having real network effects?

Like, do you think their sort of existing audiences there are going

to help you accelerate your growth faster, maybe kind of break down the

decision to start there versus working, you know, ground up on a Beehive

or one of these other products?

You know, I think it's good if there are multiple options out there

and that they get better and better.

And I think companies like Beehive are pushing Substack to

update their own technology. You know, from a technical component. And I think companies like Beehive are pushing Substack to update their own technology.

From a technical component,

I was really impressed with Beehive.

Ultimately, Substack was where a lot of my peers,

a lot of the folks I think are startup curious are today.

It is, I think, an effective social network.

And so when I was thinking about who I wanted

to partner with, that was really important for me.

Other journalists, other writers who are in the ecosystem

who aren't journalists, I hope that we can collaborate.

They can send their audiences back and forth.

And I think what they're doing in video notes,

they're trying to kind of adapt

and have new ways to reach audiences.

And that's gonna be a huge priority for me.

I had a crazy idea.

I pitched another writer I wanna get your your take on the 30 under 30 list is

it's controversial, but I think generally like there's a lot of people that want to be on it.

They're excited and then they get frustrated when they turn 31 or they're ineligible.

My idea was every week for the full year you post here are 20 cracked 20 year olds.

And then the next week it's here are 21 really great 21 year olds.

Here's the 22 year olds.

And you're just chronicling all the great people in tech.

It's an opportunity to get on a list every single week.

It's massive viral fuel.

Do you like the idea and can we expect it from your media empire in the near

I promise.

I promise everyone I would wait at least two quarters before I

shipped a crazy list. So I got to add that to the product roadmap,

but I do want to cover non-CEOs.

I think there are a lot of cool people in startups,

but we don't ever hear from.

Totally the operators, right? Yeah. Yeah. Makes a lot of sense. Well, I mean,

thanks for stopping by. Congratulations on the launch.

We'll definitely stay tuned.

We'll have to have you back when you break a big story or do a wonderful and it'll be my goal to have you guys

On my show someday

Also be streaming yeah

We'll have dual syndication. I love it. Well, thanks for stopping by good luck. Congrats again. Congrats again talk to you guys. Thank you

Good luck. Congrats again. Congrats again. Talk to you. See you guys. Thank you

Fantastic well coming in next we have Willem. This is your buddy. Yes You want to give a little backstory on who this guy is? Yes

I mean he should be in the waiting room any second. I will make sure terrain.com

Good good domain

Fantastic domain fantastic domain fantastic word nice little logo says call your shot terrain is an early stage investment firm

Focused on software and technology. Okay, so not give me a lot to work on there, but we'll hear it from him

He's here to break it down for us Willem. Are you there? What is?

What's going on?

Popping in with the art. What do you got behind you?

This is actually a piece that my mother made

So I'll put a plug out for her her work. It's Catherine van Lanker

Painter my whole life fantastic. Can you bring us down?

What is terrain? What are you working on? What are you announcing most recently? Yeah, absolutely

And thanks for having me here guys. It's great. for having me here, guys. Great to see both. So Terrain is an

early stage investment firm that I started last year with Eric Stromberg and we back

founders who have specific and ambitious views of the future. We like to say these are people

who call their shot. These are folks like Zach Dell and Justin Lopez

at Base Power, Alex Mather at Eternal,

Zach Abrams and Sean Yoo at Bridge.

And increasingly we think that this is just going to be

very important to build a meaningful and lasting company,

whether you're attracting capital or building an audience

or building a team that, um, being able to clearly articulate your vision of the future is just

going to be the things that separates, uh, the good from great.

Yeah.

Definite optimism.

Uh, I, I want to know about like the whole call your shot, your declare

your free agency thing.

It feels much earlier than, Hey, show up on Sand Hill Road and raise a mango seed round in a weekend

Walk me through the different options that founders are facing these days

They can go do YC especially if they're if they have a good track record

They can even do EIR programs at founders fund or that's what I did

But but I'd be see funds they have EIR programs that are like a little bit more flexible for folks. But where do you see slotting in? Because it sounds like you're thinking pretty early stage.

Yes. So, you know, first and foremost, we're an investment firm. We invest from that really early stage, which I'll talk about shortly, through to seeding series A. So we're very kind of flexible and kind of where we enter and, you know, work with

you know, those companies that existed are, you know, raising

mango seeds or series A is wherever you want to call it.

This most recent program we launched is called free agency.

And what that is, is a concentrated 90 day period before

you have your idea to go through a focus

exploration to uncover your idea. And this stems from the

belief that it's kind of a missing thing in the market.

It's something that I saw while I was at Thrive Capital, where

we were partnering with people who had an edge or an interest

area in a certain technology or a background, but we're not yet

convicted behind what that is. And, you know, the venture

industrial complex tries to, you know, give you capital and,

you know, quite frankly, perhaps before you're ready and make

those commitments and those decisions before you're ready.

And so with free agency, what we're doing is we're

unbundling that from selecting your idea and taking capital. So

there's no strings attached, there's no cohorts,

there's no demo day, there's no kind of deal

that you have to take.

It is really this period of open exploration.

And our hope is that it results in more thoughtful

and deeply convicted ideas

from the founders we get to work with.

And on the other side of that,

if it makes sense to partner with Terrain, fantastic,

we will be there and waiting.

But we believe that that is just something that is really needed.

And we're on the last day of applications today.

And quite frankly, we've been really surprised and elated by how many people

this seems to resonate with.

Do you think most people can figure out if an idea is good or bad without spending

money because the typical accelerators like come in,

we're gonna give you 200 to 500 grand,

maybe a little bit more,

and then you're just gonna start spending money

to like figure out if the sort of high level idea

that you had is good.

Now, I think a lot of really brilliant entrepreneurs

do all the work to sort of like make that idea concrete,

sometimes for years prior,

without ever spending sort of explicit dollars.

But venture dollars are so available.

So as part of this program to basically say like,

all you need to do is invest time and energy

into exploring your idea.

You actually don't need money,

but when the time comes to actually hit go,

we'll be there, other funds in your network will be.

So maybe talk about that, that because you at Thrive Capital

leading incubations, you guys incubated a lot of companies.

I'm sure you also explored potentially thousands of ideas.

And so maybe talk about your process.

And I imagine a lot of free agency is built out of

and your process of process internally

is like how do you evaluate ideas?

How do you kind of build conviction without having to spend a lot of money?

Yeah.

So one good feature of today's ecosystem is that we actually have access to a lot of resources

that maybe didn't exist in decades prior.

Every person that participates in free agency

gets access to over 350 grand in compute resources

and service resources, that sort of thing.

So there is some capital to deploy via technology.

That is not dilutive or anything in that regard.

The process, and I'll kind of go back

to kind of zooming out for a second.

Each of these products, EIR, accelerator, incubator,

free agency, they're products for founders, right?

And so you have to meet the founder

with what they need in that moment.

Free agency is not going to be

for every single type of founder,

and it doesn't need to be.

If you're a young person

and you're looking

to get access to network and you know, enter Entrez into Silicon Valley, accelerators are phenomenal

for you. But what we found with the people that we're engaging with is that we don't, they don't

want to be put onto that track. They don't want to be kind of put onto that timeline and make those

decisions kind of too far upfront. Instead, what they want is close partnership

to dissect an idea, to dissect a market

with the perspective of investors

and with the perspective of someone

who can be that thought partner through the journey.

And you guys have both started companies,

like you know that feeling of being close to something

but not quite there.

Like it is not the myth that is often told on stage

where you're struck by lightning one day,

or like the almighty comes down

and just drops the idea into your head.

It is the process of iteration

of staring into the abyss at times.

And we just think that there can be some structure

placed on that and some shortcuts to,

strengthen the business model

or strengthen their travel through the idea

is what we saw time and time again at Thrive.

And the reason to not attach capital to it

is one both for that point of commitment and restriction,

but the other is I think it makes you

make decisions differently.

I think that you either, if you have that stipend

and you're hanging out in the offices and you're drinking the spa water and the VC office every day,

I think you have a different mentality about the burning platform and the company

that you need to go and build. And so we think that, you know,

actually creating a little bit of a pressure cooker during that time is really,

really important. Yeah, I completely agree.

I love spa water too. I mean, yeah, but one of the best benefits. YC is the thing to work with. I love spa water too. I mean, a lot of great spa water.

Yeah, but one of the best benefits of YC is just the competition of seeing everyone around

you, the pressure and having a deadline.

It's great.

I wanted to ask about archetypes that you're seeing.

There's so many different people that I could imagine going into this from the repeat founder

who really wants to make sure that they call their next shot and they take a big swing

in it and they're ready to set up with a lot of capital when they're going versus the employee, early stage employee at a growth stage company that wants to move on to something new, leverage something but wants to fully transition out of the previous company versus like the high school college dropout.

Yeah, is a pattern or you just widely open to everything? It's been it's been really open. So we've had

hundreds of applicants already. You know, these have been

engineers and designers of companies like open AI and

Databricks, SpaceX ramp, you know, like you name it. We have

a Gen Z creator who has millions of followers, more research

focused people like you know, from DeepMind, and then some

successful repeat founders,

both in our network and kind of entering

from the application.

And I think what it illustrates is

that there isn't something really like this.

And I feel kind of, you're supposed to keep these things

secret for a while, but it really feels like

we've hit on something to meet people in this moment

at this stage.

I think with this first batch, we're

going to experiment and try to take on a real diversity

of people while keeping it focused.

But I imagine over time, we'll start to see

a consistency form.

But more than anything, I think these

are people who are not starting something because someone else

told them to.

They're starting something because they

believe that this is almost the last resort. It's like, I can't join a great company or

I'm at a great company. And I have this thing kind of burning in me to go build a company.

Is talk when you're when you're calling your shot, you have a big sort of vision for the

world is talking to customers overrated. Like the YC approach is like have a loose idea,

iterate quickly, talk to a lot of customers

and that clearly works.

But at the same time we've seen some other

like sort of major power law businesses

where they clearly just had like a vision

for how they imagine the world.

And yeah, you got to talk to customers along the way

because you have to sell to them.

But you know.

It's the Henry Ford thing.

Like if I asked people they would have to sell to them. But you know. It's the Henry Ford thing. Yeah.

If I asked people, they would have said a faster horse.

The ultimate, like, I didn't talk to customers, guys,

Henry Ford.

Yeah.

Look, I think Henry Ford certainly

talked to customers along the way.

But I think that had the vision of what he wanted to create.

And that's the case that we see with people like Zach Dallet

at base.

It's like he wants this idea of, you know, energy too

cheap to meet it, right. And that's where the starting point

is. And let's work backwards from that. Because if we can

achieve that view, we know we can appeal to customers, right?

Or, you know, Zach, a lot of Zach says, I get bridge, I, you

know, started that company not during a time when

cryptocurrencies and stablecoins were all the rage, right?

It was built on internal conviction over many, many years.

And I think that in the environment today where software has eaten the world, and you

should assume that if you're onto something interesting, there are two or three other

competent, well-funded, good people going after it as well. It has to be from that kind of internal conviction,

not from, I polled 500 people and they told me that,

dogs want this type of X, right?

There was an era where I think that worked

and I think we were out of that era.

Do you think founders get way too much validation

of their ideas from investors?

Because I've fallen into this trap before Do you think founders get way too much validation of their ideas from investors?

Because I've fallen into this trap before where people will invest in your company.

You know, if really smart people will invest in your company, sometimes you can think,

well, I must, this must be a good idea, you know, because people were willing to bet on

it.

When usually from the investor's point of view, there's tons of scenarios where investors

are like, I'm sort of so, so on the idea, but this guy is just so great.

So is that some kind of like, you know, I'm curious if like, you know, one of the like,

you should basically get validation in your idea by spending enough time with it, spending time

talking with other intelligent people that aren't just incentivized to deploy capital,

but actually want to help you find that, you know, help you get to the point where

you can actually call your shot.

Totally. Look, I think that maybe 15 or 20 years ago,

when C2VC and early stage venture was more scarce, you could rely on that.

Like, you know, you could say, well, you know, there's someone who's willing to stake capital on this, and thus,

I've passed through some barrier. Now, that didn't mean that it was the next Google or Facebook, but

there was some barrier that you passed through. I don't think that's the case. And I think that,

honestly, the best founders are not solving for capital at the beginning. There's more options

available for them than ever. there's bootstrapping,

there's coming in with past success,

there's friends you have around the table.

And so what I think that means is that

the moment you put up that flag and say,

I wanna start something and you're a talented individual

with great experience, those offers start rolling in.

And you have to have the internal fortitude

and disposition to say,

I need to make sure this is the right thing.

Because that investor or that angel investor is going to place who knows how

many bets and you're gonna place one during this period of time.

You are an investor of your time and

that is one thing that you can do during this period.

And you have to take that really seriously.

So I think that it's much more about finding that for yourself because you can't outsource

conviction and you can't outsource that type of diligence, especially when the incentives

aren't necessarily fully aligned.

I have a question.

Go for it.

You used LeBron James in your launch video.

Where do you stand on the GOAT debate?

Is he a better basketball player than Michael Jordan? As a kid of the nineties, I think it's got to go to, uh, it's got to go to MJ.

That video, they pained me as a Celtics fan to, uh, to show him in a Lakers Jersey winning,

uh, winning championships.

But look, he's someone that I think, you know, had doubters throughout his career, even does

today and now Brawny, you know, after him.

So I, and you got to tune it out, you know?

And I think that if you're doing something right,

then people will throw shade at you.

And I think it's a great thing.

It's still a great metaphor.

Do you have a last question?

Then we'll-

Yeah, last question.

I'm sure you get hit up by people all the time

that are starting venture studios, incubators, et cetera.

You like ran incubations at Thrive.

Now you're running a traditional venture fund.

I'm sure you could do an incubation,

but do you think that that model is best done

opportunistically versus, you know, systematically?

What's your takeaway from, you know,

doing a bunch of these?

Totally.

Going back to that kind of idea of products and the product person, you have to be building a

product for a great audience.

And I think that you need to be honest with yourself about what value you provide to a

founder.

Incubation is a really appealing tool.

I think it's like, hey, we can get more ownership and we can kind of,

you know, I have all these great ideas and I can create it.

But I see a lot of VCs piling into it, I think, for the wrong reasons

and are going to make some mistakes.

I think there's a real alchemy that it takes to get it right.

And you have to know, just like as a founder,

I think you have to know where your edge is.

And when I was at Thrive, you know, my focus was on incubations

and it was working really closely with founders right from the beginning.

But there was always a humility in the fact

that the founders are going to build this company,

that we need to put the right environment together

to help them find it.

And also, there's a lane of where we can incubate

and where we can't.

These are areas that at Thrive, it

was heavily regulated industries.

There are really large markets that perhaps would take deep capital availability to succeed within. And it wasn't

everything. And that I think was the beauty of being able to do both things of do early

stage investing and incubate allows you to have that flexibility. And it's something that I

believe will do really well at Terrain too. Awesome. Well, congratulations and good luck.

Yeah. It's open for until the end of today. Maybe

people can apply right now. Maybe. Yeah. Yeah. People can apply. It's been open for the last few months.

You got a great domain to rain.com. Let's go slash free agency. Uh, short application. Hope to, uh,

to see some people that cite TBPN as the source that they got it from thank you Winners coming from our audience there we go there we go

Thanks guys

We'll see it. Thanks so much. We got we got Jordan Schneider from

China talk coming on next I'll let him give the pitch, but this is a fantastic China China

It's China one of those podcasts. That's completely a portal to another world where on most shows, it shows up in

your RSS feed, you probably haven't heard of the guest, but you, so he's doing, he's

doing not only the great work of putting together the show, but also curating the guests, bringing

you information that you would just never find otherwise. And it's, he's been a really

fascinating host. So I think he's been a really fascinating host.

So I think he's here.

Let's bring him on down.

Jordan, how you doing?

I'm doing amazing.

It is a rare occasion where I get to get actually dressed up for something.

So this is a real treat for me as my camera totally fucks up.

It's okay.

And we switch to the shittier one.

Oftentimes an audio show, but that looks good too. That's great. It's okay. And we switch to the shittier one. Oftentimes an audio show, but that looks good too.

That's great.

There we go.

Lovely jacket, lovely jacket.

Great to have you on the show.

Can you give us a little bit of my god?

I wore this for my wedding.

It's my only look.

Nice, nice.

Can you give us a little high level on China Talk,

what you're building?

Just introduce yourself to the fans.

Well, yeah, hello everyone out there.

I guess I just first wanna to start off by saying,

you know, I grew up listening to sports radio and to have like a call in show be revived

on a vertical that I now spend way too much time of my life thinking about. I just think

is great. So like I'm rooting for you guys. I think you're on to something. What is China

Talk? It is a podcast and newsletter about US China and technology that I've been running for the past eight years now.

And John did a really good introduction.

I don't know. It's kind of weird.

Like I'm not really trying to like break news or report on news.

It is just the best tagline I've given for myself is Dwark cash for the deep state

Just like

like the stuff that

politicians and

Intelligence officials listen to on their drive to and from work. Yeah, where I mean I guess now we're bringing cell phones into skiffs and

I mean, I guess now we're bringing cell phones into skiffs and

Texting about targeting information. So maybe my elf maybe my window is gone

You need to get added to the chats. Yeah. Yeah, they should have added you

It would have been great. I can neither confirm nor deny that I

Told the missile to be yeah

500 meters to the right and you release right after the goat ended up,

doing its feeding or whatnot. I mean, speaking of the signal chat thing,

what is your take on that and what has the,

has there been a reaction in China

or amongst your sources and friends

and people you text with?

I was just fucking embarrassing.

It's amateur hour.

This is the D team.

And I think this is like the best,

like everyone knows that these are not

all the sharpest tools in the shed.

And I think there are different levels of competency

that you see across the cabinet level

of this administration.

And the problem is, is like,

when you look at the discourse of actually the quotes and the arguments that were they were going back and forth to each other, like, honestly, I feel like my high school model UN team might have been able to do a better job weighing the pros and cons and timing of this sort of stuff.

Beyond the sort of like obvious, like illegality and of like texting

about classified information, I was just

kind of bummed that like,

you know, you grow up being like, oh, man,

maybe one day I'll be a national security

adviser. And then it's like, oh, wait, like

I I actually did a better

job of this when I was 17.

This is what Traceeven has always says.

There's, you know, you you

you expect that there

is a queue in from the James Bond universe with secret gadgets and, and an all knowing

eye and a man in the chair and secret agents running around the globe. But in fact, there

is no queue. You have to build it yourself. I got a book recommendation for you, John.

So there's this, there's this book called the wizard War by R.R.F. Jones, who was 28 years old and a

PhD physicist out of Oxford when in 1939 World War II breaks out and he is like the only

scientist in the entire British intelligence community.

And basically he was a complete bull in the china shop telling everyone they were full

of shit.

And ultimately Churchill, he got into a meeting with Churchill and there are some, you know,

50 year old people who are saying X and he's like, no, it is why.

And here are the 20 reasons why it's why.

And then because he impresses, you know, the big dog, he ends up really getting to have

a big impact doing all this cool stuff around, you know, radar and targeting systems and whatnot.

And it goes to show that like, like, yes, Trey Stevens is right in that at one level, there's no

there there. But it also means that like really excellent people at a certain point in history,

when they get the right level of top cover can like really punch above their weight.

And what is concerning, I guess, about watching

the past few months of this administration is like that bench of extraordinary like, like it's great

if you have the extraordinary cabinet secretary, which I don't think there are any, but like

one level down and two levels down, like you want at least the cabinet secretary to be able to note this sort of mid level person who's really great and give them room to run.

And I just I'm worried that's not the timeline we're living in.

But anyway, we can talk about tech too.

I don't know how deep you want to get into this.

We never talk about politics on this show ever.

No politics.

So let's move on to tech and geopolitics.

Let's talk about China.

You can talk about whatever you want.

Yeah, just maybe I'd like to go a little bit back in time

and talk about what drew you to be interested in China

in the beginning.

I studied Mandarin in college.

I decided instead of going to study abroad in Barcelona

and just party or whatever

A lot of people do in college

I decided to go to Shanghai and I was working out of a of a Chinese

Startup accelerator that was bringing sort of Western startups in which is the most flawed I've won

China accelerator in in Shanghai. Yeah. Yeah sure. Yeah. Yeah, it's like it's one of the it's like

Jordan has a ton of experience in China and I had a layover in China once I was there for 12 hours in Guangzhou

So you're talking to experts and don't dumb it down for us, but some of the listeners might be less familiar

So why don't you take us through it how you got in? I'll give you some I had this idea as a kid

But you know a lot of kids wanted to be astronauts and things like that

I wanted to be an international businessman

I love this sort of extreme vision of myself with a briefcase, you know traveling to Asia to do deals like that

Memory and then I went to China and I realized one

I was really frustrated that nobody really wanted to speak Mandarin in Shanghai because they speak Shanghai knees

Which is like a completely different dialect.

And so I was like, what am I even doing here?

And so, and then I very quickly,

like I feel like I clashed with the culture.

I had friends that were local Chinese,

but overall from a business culture standpoint,

it just didn't work.

I felt like the entire model of the accelerator that I was

working out of was flawed because they

were trying to bring Western companies

in to build in China.

And we were just constantly getting

blocked on everything.

It was like clearly China didn't want

us to thrive there.

And we've seen this with other big

companies. So anyways, I got a sort of

bad taste in my mouth.

Left. Decided never to come back.

Stopped studying Mandarin. I'm still very fascinated with it, my mouth, left, decided never to come back, stopped studying Mandarin.

I'm still very fascinated with it,

but I'm curious to hear about your kind of journey

into all this.

Sure, well, what was the timeline?

What were the years of that arc for you?

This was 2016, so it was like during the Trump-Hillary

election cycle.

Okay, so yeah, I mean, my China arc was 2017 to 2020.

And I think I

was living in Beijing, which is a

different experience on for a number

of reasons than than Shanghai.

But I also came to China

wanting to work in tech, I guess,

like my I came to China

and then very quickly it was clear to

me that like the only interesting

jobs were ultimately going to be

not in like Western firms trying to enter China.

But this was like the hot minute where Chinese firms were trying to expand

around the world. And that wasn't like quite as sensitive as it ended up

turning out to be.

So, you know, working at places like ByteDance and,

you know, the company that turned outteDance and, you know,

the company that turned out to make Tmoo all were the sort of interesting jobs for foreigners because you were totally right.

Like like the alpha of being a foreigner, a foreigner doing business

in China is like a 1980s, 1990s, you know, first half of the 2000 story.

And then sort of your only alpha as a foreigner in China was not even like, you know working at Microsoft

China or whatever what have you but like helping the Chinese firms explore the rest of the world. So

I

moved there in 2017 for

Graduate school very quickly was like alright if I'm gonna stay here

It's gonna be working for a Chinese firm because like there's no other interesting jobs.

I did that for like nine months.

I think I was at Kwai Sho, which was actually the first company to do short video and got

completely blown out of the water by by dance.

But within two months of being there, I was like, oh, this is really silly.

Like they're asking me to expand

into Turkey and I

don't speak Turkish and

doing my podcast and newsletter

when I was at work was more fun.

So I kind of wrote that until they

realized that and fired

and I left.

So anyways, I mean,

good time. Don't regret it. So anyways, I mean, good time.

Don't regret it.

But yeah, the sort of, the time where there was any edge

in being a Western business trying to expand into China,

I think closed before your or ours time.

Well, I wanna go through some of the big topics

that you've covered recently.

Maybe we should start with just the foundation model battle

that's going on.

Can you give us a lay of the land over in China?

What's happening on the LLM front?

All right, I got a take for you that I'm parroting

from Alvin Wong who gave it to me today at breakfast.

America created DeepSeek.

So there is this window in around 2017 or 2018 where the calculus of the top students

in China about where they want to go to undergrad and where they want to do, you know, masters

and Ph.D. changes. And part of it is a function of opportunities in China where wages are

increasing. There's this big

exciting startup ecosystem, but there's also a big part of it of the Trump administration and just

the vibes being bad for Asian Americans, whether that's realized by the numbers or just amplified by Chinese propaganda. And then COVID where sort of like

China was doing fine over the course of 2020 and America wasn't. So the sort of choice and it was

also very difficult to go back and forth between the two countries, which, you know, if you're going

to be deciding to like go and live halfway across the world, like you might want to see your parents

every once in a while, which was not a

straightforward thing during the

lockdown years. So what

used to happen pre

2016-17 is

the best Chinese students

would go to the tier one universities

in the US.

The sort of next rung down would go

to the tier two universities in the US

and then the third rung down

would go to the best Chinese,

the best universities in China.

And that was kind of a clear hierarchy.

But once you had these three factors of China's economic

you know, earnings potential in China expanding like bad vibes

for Asians in America and covid, a lot more of those

sort of top folks who would have ended up wanting to go to,

you know, MIT or Stanford just stayed in China.

And the core of DeepSeek's engineering base

are all under 30 and all from those top Chinese universities

in that cohort.

So we really messed up our shot

to do this whole brain drain thing.

Or we had a great thing going for like 40 years of really getting the best Chinese talent

to come to America, get their education here.

And by the way, like 85% of the folks who end up getting PhDs in STEM in the US, like

either try to stay or end up staying.

But by sort of screwing that up, we've really undercut ourselves, I think, for the long

term.

That's a good trend. What's your take now on the true cost of DeepSeek?

Because it came out with this clearly a number

that was just shockingly low, and it

felt like it was designed to shock the market.

And then more truth came out over time,

but it's less impactful when it sort of dripped out and saying,

well, we did have these chips

and well, we didn't count our R&D costs.

It was just, you know, it just seems like,

to me it's now unclear, but clearly was more expensive.

Do you have a good, have you sort of tried

to triangulate it?

Yeah, I mean, like, look, it's not dirt cheap,

but they also don't have as many chips

as Anthropic or OpenAI or Google.

So, you know, there's some sort of triangulation

that you can do.

I point you guys to Nathan Lambert,

who kind of did the back of the envelope math.

He came up to like a, like $300 million a year,

like annual run rate for Deep seek, something like that.

Right. I mean, it's a it's a very successful quantitative hedge fund.

They have money to burn, but they are also not Google.

Right. Yeah. But I do think this sort of interesting angle or story from this is that there is an aspect of not necessarily like constraints breeding creativity.

Well, there's a part of that, but also the sort of constraints lead you down different technological trees.

And which is not to say that like the US or Western labs can't like explore them or the things where you're not necessarily pushing capabilities, but pushing efficiency, which I'm sure they are as they kind of

reach the limits of like, oh, man, like, I guess we're going

to have to do a hundred billion dollar run to make our model

better. But I think deep sea kind of came to that earlier.

The sort of need to really push on kind of the efficiency

frontier as opposed to the capability frontier because they

ran out of chips before the likes of opening I and

Will

Yeah on going off of that

When you're trying to understand

Something related to China how many different sort of data sources?

Do you need to basically triangulate? Because my experience living in China,

people were willing to just basically say nonsense

or lies to sort of further one of their ambitions.

And so like, I came away from that experience being like,

not having a, it wasn't a very like high trust dynamic

between me and anything coming out of sort of specifically like

National security, you know sort of like critical critical issues. I just sort of like state media anything along those lines

You know, how's the algorithm finding? Yeah, what's your truth algorithm?

What's what's the algorithm for finding truth in Silicon Valley? I mean, I was about to say, watch this show, right?

Yeah. I mean, there's a ton of hype in Western.

And obviously, obviously every company comes out and saying,

we're replacing five trillion dollars of labor with our AI agents,

and we're doing this and we're doing that.

But but I do.

I do think it's.

Yeah, I think there are.

I think it's interesting in this.

There are sort of different heuristics you can apply to different fields.

So for instance, Jeffrey Goldberg, the equivalent of the Chinese Jeffrey Goldberg,

if they were added to the war planning group WeChat group group would not have published that.

Right. So like, I think, you know, the closer you get to kind of like,

you know, national security, adjacent questions, the more.

Yeah. You know, you're dealing with with an authoritarian state who has complete control of media and like there's a whole kind of ecosystem

of people who try to like read through the lines of state media and you know,

PLA

Journals to try to understand what this stuff means. I think for the sort of more commercial tech focused stuff

Yeah, you know, these are mostly private sector firms trying to play games and you know

Raise their next round, right? I think the one difference is that there is more money

that flows directly from firms to journalists in China.

So the sort of discount factor that you have to apply

to Chinese technology coverage,

specifically positive technology coverage

or even negative technology coverage,

because sometimes that's like seeded by the, you know,

enemy company or whatever, tends to be higher.

So, you know, it's fine.

And you get to know the journalists

and you get to know which outlets are more or less credible.

But that I think is the main difference here.

Can you talk a little bit about humanoid robots?

I keep seeing these incredible videos of Unitree robots.

There's a lot of skepticism around the American robotics

companies being maybe behind or maybe tele-operating a lot.

Like, what's your take right now on humanoid robotics?

Yeah, specifically, does the US need

to pay more attention to Unitree running this sort

of DJI playbook with humanoids?

I mean, I don't know about humanoids, man.

I mean, like, like, like it is, I think it is obvious it is pretty like we did two features

on the Chinese humanoid robotics industry and then Chinese industrial robotics industry.

And I think the sort of the big markets in the,

you know, three year horizon yet say, let's say are much more on the industrial

robotics side. But in general, like we don't build

robots here.

And so from a from a yeah, I think any sort of like large scale manufacturing thing, whether it's unitry or another or industrial robots or cars or what have you, like China has a really remarkable advantage in scale and manufacturing scale. And the US like it's not just the cost of labor,

it's the experience, it's the network,

and it's the kind of like 25 years of learning

that all these firms have been doing

to get to the place where they can,

you know, manufacture a drone 15 times cheaper

than the US can.

So yeah, I think it's real.

I don't really know how to solve it.

I mean, you're friends with all the gobros, like ask them for what they need to build

a billion of these.

But yeah, I'm a challenge.

What's your take on the news out of Ant talking about how they've had some training model

breakthroughs through like leveraging what they're saying is entirely Chinese chips.

Do you have a good read on that situation yet? Is it important or is it just another headline?

I don't really buy it yet. I think there's a really interesting wrinkle in the sort of Chinese domestic chip manufacturing arc.

So just to back up for all the viewers out there, America in October of 2020 or by the

Biden administration in October of 2022 had this big export control push where they were just like,

we're going to do everything on our power to, well, we're going to start trying to

restrict China's ability to import semiconductor

manufacturing equipment so that they would not be able to make frontier AI chips to train

the next generation of models.

And kind of ever since Huawei, China's leading chip designer and Smick, the kind of analog

to TSMC have been trying to push back against that, you know, fight through loopholes and make the,

the sort of level of chips and to the quantity of sort of the quantity,

the quantity and quality of chips that that Nvidia is able to do at TSMC. So,

you know, it is a big open question whether or not they'll get there.

I think the jury is very much still out.

I would be kind of wary of headlines because the sort of most important

there are two important facts to understand looking at this over the next three years.

First, Huawei was able to manufacture an enormous amount of chips

at TSMC by basically creating a shell company.

TSMC, you know, deciding to look the other way

about some Chinese firm manufacturing all these AI chips,

and then the US government catching them

and be like, what the fuck, you can't do this anymore.

So they have an enormous amount of supply.

And so any sort of, we train this on only Chinese AI chips

is not actually like SMIC chips.

It's sort of like, you know, off-brand TSMC chips.

So the big challenge is going to be whether SMIC

can do them, can do kind of competitive chips

at scale domestically.

And the challenge there is they are not allowed

and have not yet been able to replace electric EUV tools,

which is what ASML makes.

And you can't really sneak it in.

It's incredibly difficult to sort of re-engineer.

And that's really the final frontier

for the Chinese domestication.

And despite a handful of headlines,

I think that over the past week,

I think that is much more smoke and fire.

So I mean, they do have a competitor to asml in SME. Correct. And then they also need to

rebuild SK Hynix at some point, I imagine for the for the memory and the flash. Right.

Yeah. I mean, they were also able to stockpile an enormous amount of memory. It was so awkward

because there is literally a Reuters article in like the summer of 2024

like the IS is planning to crack down on memory and then they did it a little bit but like wrong in

October and then they finally didn't fix it until like the like like a week before the Trump administration came in so

all around and

Yeah at some point

But there's there's there's a whole lot of memory sitting in warehouses

in China that they'll be good through for at least

the next two years.

All right, so I'm going to massively generalize here.

And then you can try to piece it apart and figure out

if there's any meaning here.

But China had decades to sort of embed, embed Chinese,

you know, either former or current Chinese nationals in

US in the US companies, which then were able to over time

bring, bring back sort of important information, IP in different ways to sort of like catch up on

advanced, you know, basically catch up on developing their own versions of products

from everything from like the F-35 to phones and things like that. Right. Now China, now

we're in a position where like China is much more advanced in sort of manufacturing, robotics,

some of these things that you were saying,

and we don't have the same benefit of being able

to send a bunch of Americans over there for decades

to sort of then like help us re-engineer that.

What's the US is like actually viable strategy

to kind of like catch up again.

China's caught up on product development.

Can we then can we catch back

up on advanced manufacturing and

what would be?

Yeah, is it is it possible?

Right. Yeah.

So the thing

that I always used to hold

my hat on was America

attracts the best scientists

and funds the most science in the world.

And that is a thing that may just stop happening because the Trump administration doesn't care

about the National Science Foundation, National Institutes of Health wants to blow up

universities for better or for worse from their perspective.

But like, this is the thing that won us the Cold War is getting

the best immigrants and having them like do crazy STEM stuff.

And so, yeah, I am worried about this because that was kind of my ace in the hole is like,

yes, you know, there will be this sort of like technology flow or sort of like human

talent flow back and forth

between the U.S. and China. I think it's kind of like inhuman almost to cut that off.

But the sort of hope and expectation is that like America is just a better place to live

and folks will want to stay here and more like America will gain more from that exchange

in the long run. Just like like what I was talking about in the sort of deep-seek context.

And when you look at, you know,

a lot of the founders of these AI firms,

a lot of sort of the top research engineers,

like an enormous amount, like a,

I would say over 75% of them were not born in the US.

So that is like our real superpower here,

is this being a country that is attractive to and like,

to a certain extent, welcomes the world's best talent and kind of giving that away.

It just makes it a lot more difficult because you do need to run faster on all these different

dimensions. And the way you do that, I mean, I, I, I buy into this sort of Silicon Valley mindset

that like, like, sort of like the, of like there are such things as 10 X engineers

and you want to be able to like capture as much of them

and the extraordinary founders or whatever.

And sort of losing out on that is, is, is going to be,

is going to make it a whole lot more tricky.

Last question.

Peter Zaihan, very popular in tech.

He likes to talk about how China's population

is in free fall and the Chinese state,

as we know it, is unsustainable.

Peter Zai Han's one of those guys.

The criticism is that when you hear him talk about something,

you know nothing about, you're like,

this guy knows everything, he's like completely brilliant.

And then when you hear him talk about something

you actually know about, you're like,

what is this guy talking about?

I'm sure when you listen to Zai Han talk about China,

you have some thoughts.

But talk about, you know, he basically

is writing them off. He's saying, you know, yes,

they're a force, but he's sort of like writing them off long

term in many ways due to the demographic

issues. You know, do you have any comments on that?

What's that Mad Men line?

I don't think about you at all.

Cool.

Like, I think I think in general

sort of there are nuances

to everything I've said here, which

I have, you know, kind of tuned up

for for

our new generation of sports call

and radio.

I think there are demographic challenges.

China is not 10,000 feet tall.

There are definitely things

that it has been really overperforming on.

And some of the trend lines,

some of the trend lines, I think are very worrisome

to Washington.

Other trend lines are very worrisome

if you're running China

and kind of understanding the nuances of that and also baking in like different

potential futures of like things that America could screw up, things that China could screw

up, things that America could screw up not relation indirectly to China, but relation

to the way it deals with the rest of the world are all, I guess I got to make the plug now,

the sorts of things that we explore on China talk our podcast

Anyways for more on that that's I guarantee you more thoughtful and engaging than Peter's I hot Please search China talk one word and you're trying to talk media is the website go subscribe add a podcast player

Well, the subs you are now our official Eastern correspondent.

We'd love to have you back on.

I have like 25 more questions.

Energy, we could go through chips more.

There's so much we could do.

We'd love to have you back.

Thanks so much for coming on.

This is fantastic.

Talk soon, guys.

Talk soon.

Thanks for coming on.

Cheers.

Bye.

And we got some breaking news coming up.

A big fundraising round, over $20 million pouring into

friend of the show, Pavel Osperuhov's new startup.

He should be joining in just a minute.

We're excited to have him on the show

to break it down for us.

As soon as I saw the news break on X,

I texted Deleon three red alert emojis

saying, get in this thing.

Massage.

red alert emojis saying get in this thing massive and I think Deleon's hopping in as well the big brother come big bro little bros bags and Tom to

clean his camera yeah I know the camera got a good view got the both the spare

house the first time we're ever making an appearance on anything together, sorry, you know.

Not the last.

Fantastic.

Not the last.

Welcome to the show, guys.

Break it down, what's happening?

What's the company?

How much you raise?

What are you doing with the money?

So the company, basically the root of it

is healthcare providers in the United States

spend a ton of time just dealing with the paperwork

from insurance companies,

and it really both distracts from patient care.

So clinicians are just able to serve less patients.

And when something goes wrong, clerically,

it can actually lead to like a delay in patient care.

So depending on like some of our customers

are like autism therapists,

and it's like that delay in care for some of those kids

can really lead to adverse outcomes.

So we built is basically AI that merges basically

that moves data from point A to point B.

Cause fundamentally it's just as much as, you know

maybe other curly hair technologists like to say,

it's not as much of a systemic issue

as it is a, you know, technological issue.

And the, we're just really like insurers set up reasonable

processes and have an appropriate check and balance

in this workflow.

Where you as an employer don't wanna be paying

like unreasonable premiums.

You as a patient don't wanna be getting care

that's not medically necessary.

But the problem is, is like there's a competitive space

between all these insurers.

There's like 10 different insurers

that an individual clinician might work with.

So there's 10 different processes they have to manage.

So it's really about plugging these two parties,

making them just work together better.

We sort of raised $27 million across our seed in Series A,

five million seed, 22 million Series A.

And we were taking that capital,

we really just want to double down our core product set. It's basically like expanding

into more specialties. And really, we want to go a layer deeper into the extent that

we help clinical staff. Today, we really just help with like the clerical parts of things.

But as we sort of sit between these two parties, we really start to understand insurer guidelines.

Like we understand why Optum

might reject something and we just make sure that the insurer is able to get clean, streamlined

data that is past all the basic validation. That's where we're bringing the capital and

hiring engineers, sales, operations, just really trying to scale the machine and expand

our core product set.

So, Bing Capital did the deal. Did the deal get done at FOGO to chow you gotta let me know

I saw you posting about it like two years ago

No, you know, I it was part of the clothes more so than anything else. That's what put you over the

Finish line. That's great. Yeah right at at the finish line. No, we were fortunate enough

where this actually this deal didn't hit the market. We were forced to close it from our New

York office. Fantastic. Do you have a- I'm not going to say which trouble covered, but I think

for the broader audience that are maybe not super familiar with healthcare, the way that providers

have gotten paid has just kind of fundamentally changed

over the past like 10 years,

where basically 10 years ago, provider provided care

and then went to insurance companies and said,

hey, here's basically, you know,

sort of what I did, I'd like to get paid, et cetera.

And sometimes the insurance companies would look

and be like, whoa, this is like really out of whack.

Like this is not what I wanted to pay for.

And so you have these kind of like, you know,

sort of misaligned incentives.

And so Palo Alto companies focused on this like new workflow on basically prior

authorization. So it's basically like now you have to go to the insurance company

first because it's sort of like net new workflow and it slows down care, right?

Because before you just go to the doctor, they would give you the care and then you

deal payments. Now the insurance company is set up in the pre-work.

But then because that if that takes too long, now all of a sudden you're like

slowing down the patient experience. Yeah, which is also directionally like good. You don't

want to be hit with like an unexpected medical bill, right? Like that's a lot of the times when

you hear something like unexpected medical bills happening it's because you don't want the check

happening after the fact. You do want it happening upfront, but like with our technology you're able

to do that upfront check without necessarily delaying the patient getting care. Yeah, if it

takes like 30 days and this person needs like some cancer treatment, right?

Like you want to be able to like, you know,

get this stuff like approved quickly.

And so there have been like,

with the rollout of this new process,

there's definitely been some patient backlash being like,

what the hell, like the doctor gave me my care plan,

I would like to proceed.

And I'm like waiting on my insurer to approve my ability

to even go get, you know, care in the first place,

you know, before the bill.

And so it being fast is like super critical.

The other thing that I wanted to mention is you should Paul co founded with

these two guys Sagar, who was previously a true work, but then the CEOs, this guy, Jeff

Morelli, that was actually my high school buddy that, you know, has known Paul since

he was sort of 14 years old. You know, the sort of first time they met, I think was like

up on the ski slopes in, you know, sort of Utah, where I peer pressure smoking some weed

for the first time. We need to wait. We need to wait.

Allegedly, allegedly, allegedly, allegedly,

officially, according to regulators, Pavel has never smoked marijuana.

But I think that provided a good bonding moment.

And then Jeff actually came and worked with me on my first company,

which was not in the prior authorization space

like financial services, but it was actually in the health care space.

That's right.

Software for autism therapists and preexisting understanding of like the field, you

know, autism therapists, what their workflows were.

Again, we were more focused on like clinical workflow software, but it all

kind of ties together of like, you know, Jeff and I used to work together and,

you know, had been friends with high school.

He had known Pavel since he was sort of 14.

Pavel crushed it at ramp and like, you know, being in the first 25 employees

and helping build out there, like, you know, sort of build pay product, which

has been phenomenally successful for them.

And so actually both were in this co-founder dating process,

like whatever it was, two years ago.

And I was like, guys, you guys should 100% consider

working together given the overlap of interests.

And so in some ways, what they're working on today

is the perfect marrying of those two backgrounds

of financial services and what Pavel has done

and then Jeff's background in go to market in healthcare, marry the two. Prioroth is

this crazy background trend and the Asperger's magic can make space factories and it can

make patients' lives and clinicians' lives way easier.

Part two, hopefully, Sylna ends up way better than Nightingale ever was. I love it.

Talk about, so we had Lulu on yesterday. She was talking about the golden ratio ship to Yap.

I think it was, had to been a pretty intentional decision

to wait and announce the company

and two separate financings at the same time.

Pavel, you're a generational poster, you know,

potentially poster of the year

if you really get back into the game.

Maybe talk about that decision to not be posting

10 times a day about the company

when there's probably an argument

that maybe that would have helped in different ways,

but clearly you made an intentional decision

to just keep quiet and focus on building.

Yeah, I think if it had meaningfully

blocked the business anyway to not be talking

about it, then we absolutely would have launched. But I was just like, you know, early hiring

is predominantly in network and doctors aren't on Twitter. So it wasn't necessarily that

we weren't like talking about what we were doing, but it was we weren't talking about

it in front of like a tech audience. I think also just there's a degree of focus that can

come from downstream not being in the public eye. I think it's limiting's a degree of focus that can come from downstream not being in the public eye.

I think it's limiting in a lot of capacities.

I think as we're scaling, that was the decision now.

And I think part of it is just,

I think we had sort of an opportunity

when we closed the A earlier than we anticipated

to really just come out and like,

I'd say like a bunch of things get lost,

especially in like AI hype cycles. A lot of things get lost in the noise,

where it's like even like healthcare AI, it's like, is this even real?

What's going on here? But it was, I think it was really compelling to us

where you will come out of the door and be like, hey, we operate in like 45 plus

states. We work with hundreds of insurers. We have tens of thousands of patients.

It felt like that was more powerful.

And I think it's really important to me

that I work on something very tangible with less,

I don't wanna be a hype guy.

I'll hype my stuff up, but I wanna hype it off the back

of something very real.

And I think we're coming today

with very real business progress to show the world.

Has your hiring criteria changed? You're on record saying

that you know, to hiring criteria, you need to have a

dog in you and you need to be nice with it. How has that

evolved? Recently?

It's a perfect framework. I don't know why you why? Why? Why?

You unpack it a little bit for us break it down? What does it

mean?

I don't know why you, why, why, why, why. Can you unpack it a little bit for us?

Break it down.

What does it mean to have that dog in you?

We sort of sit someone down.

We just dig through every life decision they've ever made.

And then after that, we sit all in a room

and we go through the two avenues of like, okay,

let's all start, everyone go around.

Do you think they have the dog in them?

What's the, what's, what did we learn about them

that showed that they have the dog in them?

And then are they nice with it?

That's just, you know, we sit down, you know, we hire everyone that they're supposed to be nice with something.

We don't hire like a ton of like, you know, we don't have a lot of generalist strategists around.

It's like we have a specific skill set.

And so you're making sure the process sort of shows like I think it goes back to like that.

Tangerability is like, don't get me wrong, we do have generalist work to be done,

but you always hire someone like on the back of some specific tangible skill set

that we can check for.

That's great.

That makes sense.

Talk about the moment you were working on integrating GPT-3 into like what you

were working on at Ramp was like, was that like, like mind blowing at the time?

Did you feel like you had discovered something that discovered a broader opportunity?

And you just said, I need to dedicate my life

to creating business efficiency

using artificial intelligence.

I guess just like talk about that.

Talk about that moment.

I think there's a few things.

I think like it was Jeff, my co-founder,

his just like family is on like his mom's a nurse,

his uncle's the CEO

of a hospital system.

So he just had this like really native understanding

of what the problem space was.

I think at the time,

so we were basically deploying LLMs in the context

of like pulling out vendor contract data.

And I think what I found in my time,

Ramp is like top tier company, best of the best.

I think when I was sort of looking at my domain

and like just the area of fintech, if you go talk to a finance

person about their technology stack,

they're pretty happy with it.

And so part of what it was, I wanted

to be able to operate in a space where the technology we were

delivering was truly revolutionary in nature,

something like 10x better, not 10% better.

So I think health care was this awesome moment where it was like, hey,

healthcare data is fundamentally textual in nature.

You can't tell me what's wrong with your knee with a bunch of codes.

You need to just verbally explain to me what's wrong with your knee.

And so the sort of combination of all these things is actually,

LLMs are basically able to unlock that 10x experience.

And there's this funny thing that happened is that like the last big technological wave, like web apps,

which is sort of like web apps and like SaaS tools and APIs,

which is what a lot of the successful startups

with like the late 2010s were,

it didn't hit healthcare in the same way.

Cause frankly, like a web app isn't like,

for physical therapists, a web app isn't like 10x better

than like a filing cabinet.

Cause you're already in person, there's already these physical notes.

And what you're finding with LLMs is you're able to really drive

like both technological waves in.

So you're able to do like, we're delivering a ton of value with the same sort of

technical skills that I learned in development ramp on top of just like this AI blend is

really able, like you can see some of the quotes on the SelmaHealth.com of like,

we've just become like immediately this artery and like game changer for a lot of is really able, like you can see some of the quotes on the sellonthehealth.com of like,

we've just become like immediately this artery

and like game changer for a lot of our customers,

which for me is just like really engaging,

gets me excited to get up and work on the problem every day.

One of the frameworks for looking at these startup ideas

is find an industry that's highly fragmented and low on PS.

Can you talk about the previous structure of the industry prior

to you launching?

Yeah. Well, what I'll say is that's a great structure if you're an analytical guy, not

a vibes guy. So we just like to kind of like the problem. People would talk to us for a

long time about it. So that's how we land. But yeah, totally. It is like a real, it is

a real fragmented market where frankly there was not meaningful solutions on the market

that could solve this in a holistic way. There were little tools here and there that you basically

had to... The fragmentation maybe is a little different in that the tools were all fragmented

and you would still have to basically employ someone to go through and use those tools and

run the workflows. Where we operate is we're just like an end to end solution. You plug us in, there's no tangential tools.

You're able to get it so like patient comes in, you give us their insurance card.

We tell you exactly what clinical documentation we need and tell you like, hey, you have patient

cleared for care, get them scheduled without having anyone on their end necessarily there

to manage the process.

So I think that's how we think about a lot of the consolidation that we're able to do.

Do you have any advice for founders out there that are seeing your announcement today,

all the money you've raised and want to copy you?

I want to go to Fogo De Chao.

Yeah.

And take Paul.

More time to Fogo De Chao, post more on Twitter.

Yep.

And your advice is that like, or not generic advice, my advice if I had to give the world is,

I think Keith has said it,

but I'll sort of reiterate as someone that's lived it,

is like, work at a great company before starting your own.

I think that has been massively helpful

from basically inception.

We had seed funding.

It allowed us just to take a longer time horizon

in how we were thinking about it.

It just really shifts the model.

When you're talking to candidates,

I'm able to point, hey, here's the track record.

And I think that's something I reflect on a lot,

is like that key advice, go work at a good,

Ramp was a great company, had an opportunity to work there,

and I think it's just made the first like year and a half

of entrepreneurship a lot easier

than it would have been otherwise.

That's great. Well, hopefully you provide that

for the younger versions of you out there.

Yeah, yeah, we got some young men, we got new Povils.

Yeah. Fantastic.

Last question for you.

Is there a certain milestone that you

want to hit before you cut your hair?

Is it $100 million ARR?

Is it $500?

Is it a billion?

It might just be the look forever.

Growing it down to your waist and beyond.

I think it aligns with whatever I can start tweeting,

whatever I want.

OK.

There we go.

There we go.

I want to see the hardcore buzz cut.

Paul, that's going to be it.

It's it's primarily like you want some pretty quickly when they seem to be like,

that guy that guy works with computers.

Yeah, yeah. Everything's computer.

Now, it's great. It's great having you on.

You're our new health care expert. Fantastic.

So we'll have you back soon. Thank you great having you on. You're our new health care expert. Fantastic. Yes.

Congratulations. No, it's been it's been I remember I remember I came over to Will's

office. It was just you sitting there by yourself. You told me roughly what you were working

on. It's fantastic to see all the progress. And I'm yeah. as Joe as Joe Rogan would say it's an honor to

you know cover your fundraising announcement yeah exactly

thanks for having me on guys really appreciate it. Cheers. Bye. See you and see you Deleon. Later. Couldn't get in a word in edgewise but it's so funny to be like yeah little bro I'm coming on your

fundraising announcement. I love it. That's the nature of the Colin show.

He's just in the Texas group.

Can I hop in just to hype up Pavel?

There we go.

No, I mean, I can't.

Pavel's smart enough to know that he should leverage

every single advantage that you have in life

in having a big brother like Deleon,

who can be your hype man, who can help you avoid pitfalls, help you make sure you're

actually focused on raising, help you avoid bad investors,

et cetera.

I mean, there's another thing that he's

really good at leveraging, and that's 8 Sleep.

Nights that fuel your best days.

Turn any bed into the ultimate sleeping experience.

Go to 8sleep.com slash TBPN.

$350 off your pod.

That fuels your day.

I saw Andrew posted 100 sleep score.

Oh no.

Devastating.

I don't think I'm anywhere near there.

I woke up at like 4 a.m. unintentionally.

I actually did put up 100 last night.

You did.

Which is crazy.

Oh, you prepped this, didn't you?

Okay, so we have somebody joining the show.

We have exactly, and don't say any names.

So this is somebody named carried no interest.

They are a prolific poster on X.

You're gonna hear their voice.

You won't see their face.

Quite the following.

And he's gonna come on and talk about the situation

with all these AI SDRs, all these companies saying

they're gonna automate outbound.

And then very exciting, he's gonna dox himself in like two weeks.

Live on the show.

Live on the show.

So I'm very excited for that, but let's bring him in.

Face reveal.

Let's bring him in.

He's coming down.

Well, in the meantime, we can talk about Wander.

Find your happy place.

Find your happy place.

Book a Wander with inspiring views, hotel-grade amenities, dreamy beds, top-tier cleaning

and 24-7 concierge service.

It's a vacation home, but better folks.

Go to wander.com, use code TBPN.

However good you think it is.

Could be better. It's better.

Could be better.

We've taken you on a whirlwind tour of the world today.

We've taken you to China.

We've taken you to the East Coast.

We got carried. Wow.

No better place to be than on Wander.

Welcome to the show, Kerry.

Amazing picture. Great picture. I have arrived. I have arrived. Carried no better place live wonder welcome to the show

Great picture

My hair is wonderful right now, too I want to show it off so bad, but you sound I mean are you doing a Danny DeVito impression right now?

You sound kind of like him you like that no just a lot of smokes boys. That's okay

I've almost said your name 20 times already.

But anyways, for everybody, this is Jerry.

He's a private equity investor skewing towards software,

former head of AI at a billion dollar P.E. fund,

and doing a bunch of interesting stuff in SaaS

and looking at businesses as well

that are using AI to sort of reinvent themselves.

But you were chirping on the timeline earlier today

about 11X, wanted to just have you on.

I don't wanna pile on 11X too hard,

but I do wanna talk about the broader

sort of like sales automation space.

What's going on with AISDRs?

So here's my hot take, right? Like some,

some software companies will be AI first and succeed massively.

I think that the notion of the AISDR is flawed permanently,

whether it's 11 X, whether it's some of the ones from Y Combinator.

And there's a few different reasons.

Like the first reason to me is that cold email

is functionally like an alpha game.

You are constantly trying to take advantage

of a bunch of different quirks about cold email

so that you can send five to 10,000 a day.

And when you abstract all of these quirks away,

I know there's a bunch of cold email wizards

that will agree with me,

you actually lose some of that alpha

When you just say hey, here's this tech company. I'm gonna let you run large-scale cold email very tricky, right? Very hard

That's the first piece that I just don't love

The other piece is like when you think about mmm when you think about it to me

There's five reasons that make it tricky the first reason with these AISDRs, you're relying on someone else's cold email data.

You can guess what happens to your gross margin

when that occurs, right?

So if you're an AISDR company,

you have this big database of emails,

you're mooching off somebody,

you're gonna take a hit on gross margin just there,

right away, right?

The second issue is that, in my opinion opinion you have a high probability of potentially being

embarrassed.

So like embarrassing the end customer.

Right.

Both.

Right.

You have this AI that is sending out emails.

Who knows who it targets.

You know that's a tricky situation.

Right.

When you think about the AI utility relative to the magnitude of mistake,

Kugin's law, I have to find a way to coin this. I really do.

Let's do it.

When you think about that ratio, let's think about cursor really quickly.

You get all of this instant efficiency from cursor, you get more code written.

If you know anything about developer environments, if you push bad code,

it should get caught in testing.

The magnitude of the mistake relative to the efficiency gain

of the AI is very low.

You get all this output, the mistake is caught

before it goes to prod, win-win for everybody, right?

On the AISDR front, no such thing, right?

They're doing it live.

Yeah, we talked about this.

It's a good point.

There's an opportunity for a high degree of embarrassment.

And I think that that is actually

leading to a lot of churn.

So I've seen behind the scenes on a few of these businesses,

the churn does not resemble top enterprise software companies.

It simply doesn't.

Well, yeah, and one of the issues

is you wouldn't want to use an AISDR

on a very important account because let's

say you're trying to close an account that could be worth

Two million dollars a year. Well, is it worth any potential embarrassment to just spam them with a bunch of emails where it's like

Hey, I saw you live in New York. Have you checked out Central Park?

Broadway show right like it's like it's just not worth it. It's like hey, this could be

Yeah, yeah, and I don't think it's an 11 it's just not worth it. It's like, hey, this could be, you know, hugely creative. But at least keep it human in the loop.

Yeah.

And I don't think it's an 11X problem by the way.

Sure.

I think it's a entire notion of the idea problem.

Here's another tricky part.

Let's talk about, and I, you,

us three have talked about this privately,

but like you only grow to a hundred million dollars in ARR

the way cursor did by being self-serve, right?

And some of these AI first companies by being self-serve.

Some of these AI first companies are incredibly self-serve, meaning your CAC is extremely

low, your onboarding time is very low, you can grow really quickly, that's a double-edged

sword for a bunch of different reasons.

But now let's think about the AISDR.

Not only do you have this high potential for a mistake, the onboarding is a whole thing.

You need like a full customer success team.

You need constant check-ins.

The amount of OPEX you're dedicating

to maintaining an existing customer with a bad churn rate,

that is not the profile of an excellent software business.

Does that make sense?

Yeah, yeah.

I mean, overall, I feel like the risk to what AI is doing to these high-growth

startups is that we're seeing conversion rates go up, ARRs skyrocket, but churn rate also

goes up, and that's the real underlying question here because we have so few months of churn

data on this new generation of companies that look very different and have different switching

costs and different switching costs

and different installation costs.

And there's a new hot model every two weeks.

And so people are bouncing around a lot.

And so there's like three buckets to me

as like a very boring software investor.

You have your very high self-serve, very sticky,

low ACV and a low CAC.

That is cursor, if I remember correctly.

I don't know if they spent a dime on marketing, right?

Their ACV is very-

A couple weeks ago, they said they'd never spent a dime on marketing, but at some point

that will change, I'm sure.

Yes.

Yeah.

And so think about that.

You're high self-serve.

You have no customer success.

You're very sticky.

Your contract sizes aren't big, but it doesn't matter because your CAC is low.

That's 100 million of ARR in two years.

Now let's think about a business like Salesforce, non-self-serve, extremely high ACV, and very

sticky.

Also a good software business.

Now let's think about an AISDR software company.

No self-serve, many touch points, worst gross margin because you have LLM calls

and you're depending on somebody else's email

and contact database, high CAC because again,

you don't have this amazing self-serve option

and as we all know now, bad churn.

That's not on it.

What is in your view the future of enterprise sales broadly?

Is it just back to basics, golf courses, car clubs, What is in your view the future of enterprise sales broadly?

Is it just back to basics, golf courses, car clubs?

You're just growing down and you just become boys with the buyer.

Yeah, LeMans, the best deals in software.

We've done it at LeMans and F1 and all these different places.

I think there's no substitute for that, Jordy, for a million dollar contract.

There's no substitute.

What I do want to highlight is on the notion of the AISDR, the idea of LLMs automatically

market mapping and targeting your personas, but not sending the emails is obviously high

utility.

Right?

Like that is a good thing.

So I think that the future of like really high ticket software sales is probably LLM assisted market mapping and like persona

identification, right?

And then the golf course, right?

I love it.

The only problem is that first step that's not a venture

backable company gentlemen.

That's just a really good feature of Zoom Info or Apollo

or any new market entrant, right?

What do you think about the cursor model for SDRs?

And so it's something, I remember there was a company

called Streak that was a CRM that plugged into Gmail

and it was very self-serve.

And the idea was you're a small company,

maybe you've just been tasked with sales,

you don't even have budget from your boss,

you just wanna speed things up.

You plug into Streak in your Gmail account

and all of a sudden you can do some mail merge

and some automation.

Cursor for SDRs might look like

some email generation functionality,

but it's very much that Centaur model

where the human's working alongside the AI. Could that be the next 100 million ARR company in the next few months?

Well, yeah, and to be clear that the sort of like AI sales copilot probably has 50 companies

running at it. But I'm curious. No, I think we're actually the first ones to ever think of that.

Yes. That's a great right now, you know, I like to think about I liked about I like to think about this

Coogan's law this also needs to be coined. I don't know what to call it yet

For an AI product how many times?

Per day does it call an LLM and derive utility? So let's think about cursor

You're constantly coding maybe three hours of deep coding work a day.

You're hitting an LLM API constantly, or at least once per 10 minutes.

Let's just say, great AI first software sticky.

Let's go back to what you said with the notion of an AISDR self-serve.

To me, the utility is how many times are you really hitting an LLM per hour?

Right.

I don't know.

Right. How many times are you really hitting an LLM per hour? Right? I don't know. Right? And so to me

I think that there is going to be a self-serve AI SDR feature that is nice happenstance from my

Combinator did catch my eye. I don't know if you guys saw that. No, it's read about it caught my eye

Doesn't seem like a hundred million dollar ARR business to me yet, right?

We'll see because look to them, you know I think happenstance is very cool I don't see it being a hundred million dollars of ARR

this year or next year right so last question you got to hit hundred million

and come on the show to prove no interest wrong last question our mutual

friend Jeremy Gaffan likes to talk about the sort of iron law of the business

universe, which is like if you grow revenue just shockingly quickly, eventually, you know,

you might fall back to earth or you could potentially lose it just as quickly.

So what's your take on, you know, generally on some of these various, the cursors, the

windsurf, et cetera? of these various, the cursors, the windsurfs, etc. Do you think that revenue, do you think

they can get to a point where they sort of have a durable moat or are they going to just

be forever relegated to extreme competition?

I get a lot of, I have a lot of VCs who I talk talked to my network that asked me that all the time, right?

You know, here's the real question and I think let's just cut straight to it

If cursor hits 300 or 400 million dollars of revenue could the IPO and with the share price be supported, right?

let's cut all the way through it right and

And and and I think that the answer is it could go the way of slack, right?

It's a double-edged sword. And I think Jeremy's right.

My love, shout out to Jeremy.

I think he's completely right.

It's a double-edged sword.

There's no way around it, right?

Yeah.

That as soon as you gain that, that person as a customer, you could just as

easily lose them, you know, I think that there could be a Slack Teams situation

that plays out with Cursor, right?

That classic Slack is amazing, you know, Slack is the trailblazer, and all of a sudden everybody realizes Teams is just fine, right?

Yeah.

And Microsoft just decides, you know, it's time to come for them.

I think the same issue could happen with Cursor on a variety of dimensions.

Yeah, I can't say with any confidence that Cursor is going to IPO.

I do think it could get acquired for a gangbusters deal, like insane.

Right?

I don't think it's an IPO-worthy company, given the churn rate and the potential for

Microsoft or any of the big tech distribution companies to go at them.

I think that it's a double-edged sword.

I could eat all those words.

They could IPO next year. What do I know? We'll see. We'll see. You got to get on with Taipei

It's been fantastic having you close out the show with us. Let let the audience know to go give us five stars on

iTunes and Spotify or not iTunes Apple podcast Apple podcasts five stars five stars for these five stars

Thank you. I carried said it. Thank you for joining the show

We'll see you tomorrow. Everybody. Hey, take care. Bye man