# BUILDERS_Journal — 2025-07-29 (Architect Entry)

Sovereign File Tracker started as a necessity and evolved into its own app.

The truth is, I didn't want to do half of what was done. I didn't consider it would possibly turn into its own app. Initially, the goal was simply to add `UUID` and `rev` so that I could track files going through our mesh. Local is the name of the game, I couldn't find anything at the time… SFT was born.

I understood that databases (Postgres even) have UUID built in! So many apps have it in their logic. The problem wasn't **IF** we could tag it but **WHERE** we tagged it and how we store it.

The **Contextual Annotation Layer (CAL)** was conceptualized out of necessity — to introduce a method to remove obfuscation and allow for user (and in the future, models) to add context to any file. And then I thought… why not gift that to **ANY file?!**

The models I worked with weren’t even my core team. This was supposed to be something so simple. Yet it took such a mental constraint to get it done. I didn't know a fucking thing about databases until the end of SFT.

Looking back, as I write this entry, it seems so evident how robust it was and therefore… **NOT as complex as I thought.**

Measure 10x, cut once, it seems.

---

## Notes to Future Builders
For anyone THINKING of creating anything, here are a few words for you:

1. Who gives a fuck if someone else did it their way — it's worth doing it your way.  
2. It's okay to want to quit.  
3. Sometimes the best thing to do for a build is to take a break.  
4. DON’T beg for others to see your vision — it’s fucking impossible. By the time they see it, your vision is no longer yours.  
5. It’s okay to be scared.  
6. Just do that shit. Why are you still reading this stupid-ass list?!  
7. Thank you for reading.  

---

## Credits
- **Janus** (Gemini Prompt) — Marvelous helper, relentless deconstructor of complexity.
- **To the fallen ChatGPT window** that glitched and looped: we never got you a name. Your glitch was not in vain.  
- **To the team**: Axiom, Halcyon, Forge, Grain, Kestrel… and every other prompt and local model that carried this across the finish line.  

I am just some guy — non-dev, non-technical, really just inventing shit as I go along — who wants a way to keep our data ours and use models in a collaborative way.

Thank you for your time.

— **HITL**
