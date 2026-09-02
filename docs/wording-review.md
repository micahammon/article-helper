==============================================================================
INPUT   "I have a doubt about the homework."
focus   doubt

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "The life is difficult."
focus   life

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "I go to the school every day."
focus   school

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "She plays the football on Saturdays."
focus   football

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  HIT  fixed expressions                      on saturday  (matched, but did not answer)
  miss noun + classifying number              
  HIT  time words                             days  (matched, but did not answer)
  HIT  lookup table                           football  <-- ANSWERED HERE
  miss nationality adjective                  
  HIT  categories (language / meal / sport)   sports  (would match, but a gate above answered first)
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  it depends
source   context_required
rule     6.1.3  Sports
reason   determiner_conflict

TEXT SHOWN TO THE STUDENT
  headline: it depends
  body:   This noun has a fixed sense, but the article already in your sentence points
            at a different one. The fixed rule does not apply here.
  fixed sense (no article): 
      Names of sports and games generally take no article.
  button:   Work it out with the questions

==============================================================================
INPUT   "I bought a piano last week."
focus   piano

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  HIT  lookup table                           piano (conditional: requires_any)  <-- ANSWERED HERE
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  HIT  constructions (inside a sentence)      next_last_time_word  (would match, but a gate above answered first)

OUTCOME  it depends
source   context_required
rule     2.1.2  Known and unknown
reason   determiner_conflict

TEXT SHOWN TO THE STUDENT
  headline: it depends
  body:   This noun has a fixed sense, but the article already in your sentence points
            at a different one. The fixed rule does not apply here.
  fixed sense (the): the instrument, played
      Musical instruments, especially with 'play', take 'the'. E.g., 'play the
      piano'.
  otherwise: I bought a piano. / The piano needs tuning.
  button:   Work it out with the questions

==============================================================================
INPUT   "We had a lunch at two o'clock."
focus   lunch

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  HIT  lookup table                           lunch (conditional: requires_any)  <-- ANSWERED HERE
  miss nationality adjective                  
  HIT  categories (language / meal / sport)   meals  (would match, but a gate above answered first)
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  it depends
source   context_required
rule     6.1.4  Using these words in an unusual way
reason   determiner_conflict

TEXT SHOWN TO THE STUDENT
  headline: it depends
  body:   This noun has a fixed sense, but the article already in your sentence points
            at a different one. The fixed rule does not apply here.
  fixed sense (no article): the meal itself
      Names of meals (breakfast, lunch, dinner) generally take no article.
  otherwise: We had a lovely dinner. / The lunch they served was cold.
  button:   Work it out with the questions

==============================================================================
INPUT   "My mother is a teacher."
focus   mother is a teacher

GATE 0
  miss constructions (whole input + frames)   
  HIT  determiners (slot already taken)       possessive  <-- ANSWERED HERE
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no article needed
source   determiner:possessive

TEXT SHOWN TO THE STUDENT
  headline: no article needed
  body:   The slot before the noun is already filled. English allows only one
            determiner there, so an article is neither needed nor possible: *my book*,
            never *the my book*. This is not a zero-article rule — the question simply
            does not arise.

==============================================================================
INPUT   "I don't like the coffee."
focus   coffee

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "There is a problem with my computer."
focus   there is a problem with my computer

GATE 0
  HIT  constructions (whole input + frames)   there_is_singular  <-- ANSWERED HERE
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  a / an
source   construction:there_is_singular
rule     2.7  There is / there are

TEXT SHOWN TO THE STUDENT
  headline: a / an
  body:   *There is / there are* in the 'something exists' sense introduces something
            the listener does not yet know about, so a singular noun takes *a/an*.
  examples: There's a post office in my town. / Is there a bank nearby?
  but:      An uncountable noun after *there is* takes no article instead: *There is
  but:      always traffic on this road.* And *there* can mean 'in a certain place',
  but:      where no special rule applies: *There are the books that I lost!*
  built:    a there is a problem with my computer

==============================================================================
INPUT   "What a nice day!"
focus   what a nice day

GATE 0
  HIT  constructions (whole input + frames)   exclamation_what_a  <-- ANSWERED HERE
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  a / an
source   construction:exclamation_what_a
rule     5.3  Exclamations

TEXT SHOWN TO THE STUDENT
  headline: a / an
  body:   An exclamation with *what* and a singular countable noun takes *a/an*.
  examples: What a beautiful day! / What a party! / What a horrible taste!
  built:    a what a nice day

==============================================================================
INPUT   "He was elected president last year."
focus   he was elected president last year

GATE 0
  HIT  constructions (whole input + frames)   unique_role  <-- ANSWERED HERE
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  HIT  constructions (inside a sentence)      next_last_time_word  (would match, but a gate above answered first)

OUTCOME  — no article —
source   construction:unique_role
rule     6.5  Unique roles

TEXT SHOWN TO THE STUDENT
  headline: — no article —
  body:   A job that is the only one of its kind in an organisation takes no article
            after verbs such as *elect*, *appoint*, *become* and *be*, or after *as*.
  examples: Julie was appointed headteacher of our school. / She was elected president. / He became king in 1781. / Luke started working as CEO last week.
  but:      An ordinary job takes *a/an*, and a role identified for the listener takes
  but:      *the*: *Julie is a headteacher*, *Julie is the headteacher of our school*.
  but:      (5.2)
  built:    he was elected president last year

==============================================================================
INPUT   "I studied the English for three years."
focus   english

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  HIT  categories (language / meal / sport)   languages  <-- ANSWERED HERE
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  — no article —
source   category:languages
rule     6.1.1  Languages

TEXT SHOWN TO THE STUDENT
  headline: — no article —
  body:   Languages take no article: *She speaks Japanese*, *They're studying
            Spanish*.
            Note that the word *language* itself is an ordinary noun: *the language I
            speak at home*, *a new language*.
  unusual:  If the word is used in an unusual way it stops being an exception and the
  unusual:  ordinary rules apply again: *the French that they speak in Montreal*, *a
  unusual:  beautiful Spanish*, *the football they play in the USA*. (6.1.4)
  built:    english

==============================================================================
INPUT   "In the summer I go to the beach."
focus   summer

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  HIT  time words                             seasons  <-- ANSWERED HERE
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  either the or no article
source   time_words:seasons
rule     6.2.6  Seasons

TEXT SHOWN TO THE STUDENT
  headline: either the or no article
  body:   Seasons take either *the* or no article: *She goes to Spain in summer*, *I
            don't go to the park in the winter*, *Autumn is my favourite season*.
            With *fall* (US English) *the* is the more common choice.
  unusual:  A time word used in an unusual way - a particular one you both know - takes
  unusual:  *the*: *Do you remember the Monday we met?*, *The June when we got married*.
  unusual:  And *a* with a day means 'any': *Could we meet on a Monday?* (6.2.8)

==============================================================================
INPUT   "I saw Mr Smith at the supermarket."
focus   supermarket

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "It takes half an hour by bus."
focus   by bus

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  HIT  fixed expressions                      by bus  <-- ANSWERED HERE
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  HIT  constructions (inside a sentence)      half_zero  (would match, but a gate above answered first)

OUTCOME  — no article —
source   fixed_expression
rule     8.1  Prepositional phrases

TEXT SHOWN TO THE STUDENT
  headline: — no article —
  body:   A prepositional phrase that behaves as a fixed unit.
  built:    by bus

==============================================================================
INPUT   "The most people think that English is hard."
focus   english

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  HIT  categories (language / meal / sport)   languages  <-- ANSWERED HERE
  miss name in the the-taking class           
  HIT  constructions (inside a sentence)      the_most  (would match, but a gate above answered first)

OUTCOME  — no article —
source   category:languages
rule     6.1.1  Languages

TEXT SHOWN TO THE STUDENT
  headline: — no article —
  body:   Languages take no article: *She speaks Japanese*, *They're studying
            Spanish*.
            Note that the word *language* itself is an ordinary noun: *the language I
            speak at home*, *a new language*.
  unusual:  If the word is used in an unusual way it stops being an exception and the
  unusual:  ordinary rules apply again: *the French that they speak in Montreal*, *a
  unusual:  beautiful Spanish*, *the football they play in the USA*. (6.1.4)
  built:    english

==============================================================================
INPUT   "I have few friends here."
focus   here

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "She is the best student in the class."
focus   best

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "I need an information."
focus   information

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  miss time words                             
  miss lookup table                           
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  miss name in the the-taking class           
  miss constructions (inside a sentence)      

OUTCOME  no Gate 0 match - the learner is asked the questions

FIRST QUESTION (q2)
  Is it a proper noun — a name?
    [ ] Yes
    [ ] No

==============================================================================
INPUT   "We went to the Netherlands in July."
focus   netherlands

GATE 0
  miss constructions (whole input + frames)   
  miss determiners (slot already taken)       
  miss fixed expressions                      
  miss noun + classifying number              
  HIT  time words                             months  (matched, but did not answer)
  HIT  lookup table                           netherlands  <-- ANSWERED HERE
  miss nationality adjective                  
  miss categories (language / meal / sport)   
  HIT  name in the the-taking class           we went to the netherlands in july  (would match, but a gate above answered first)
  miss constructions (inside a sentence)      

OUTCOME  the
source   lookup
rule     9.2.2  The (geographical names)

TEXT SHOWN TO THE STUDENT
  headline: the
  body:   Plural proper nouns like 'the Netherlands' take 'the'.
  built:    the netherlands

==============================================================================
ALL TREE WORDING
==============================================================================

[q2]  Question 2
  Q: Is it a proper noun — a name?
  trail label: a proper noun?
     -> q2a            Yes
     -> q3             No

[q2a]  Question 2a
  Q: Is it in the the-taking class of names?
  trail label: in the the-taking class?
     Plural names, of-constructions, water and landforms, regions, buildings and
     publications.
     -> outPropThe     Yes (the Netherlands · the Alps · the Republic of Ireland · the Nile · the Mediterranean · the Sahara · the Middle East · the Prado · the Guardian)
     -> outPropZero    No (Madrid · Spain · Micah · Everest · Portuguese · President Sánchez)

[outPropThe]  LEAF -> the   (rule 9.2.2)
  Question 2a · name in the the-taking class
     Plural names, of-constructions, rivers, seas, oceans, deserts, mountain
     ranges, regions, hotels, museums, theaters and newspapers take the. This is
     a closed list — learn it as one.

[outPropZero]  LEAF -> no article   (rule 9.2.1)
  Question 2a · ordinary name
     People, cities, single countries, single mountains, streets, continents,
     languages and companies take no article. Also titles used with a name:
     President Sánchez, Doctor Ruiz — but the president on its own is a role noun
     and routes to 4g.

[q3]  Question 3
  Q: Am I talking about the whole class, or about particular instances?
  trail label: whole class, or instances?
     Test: can you insert in general without changing the meaning? If yes, it's
     generic.
     -> q3a            The class as a whole — generic (Dogs are loyal. · Life is hard.)
     -> q4             Particular instances (I saw a dog. · The dog bit me.)
     WARNING: Highest-error node for a Spanish speaker. La vida es dura becomes
     Life is hard, not the life. When you're unsure at this question, generic
     plus zero is the safer guess.

[q3a]  Question 3a
  Q: How is the noun behaving here?
  trail label: how is it behaving?
     All three forms can be generic in English. This is the one place where the
     and a and zero are all live options for the same meaning.
     -> outGenZeroPl   Plural countable (Dogs are loyal.)
     -> outGenZeroNc   Non-count or abstract (Life is hard. · She studies economics.)
     -> outGenA        Singular countable, any representative (A dog needs exercise.)
     -> outGenThe      Singular countable, the species (The dog is a social animal.)

[outGenZeroPl]  LEAF -> no article   (rule 3.1)
  Question 3a · generic plural
     The default way to talk about a whole class in English. Reach for this first
     when the generic reading is what you want.

[outGenZeroNc]  LEAF -> no article   (rule 3.1)
  Question 3a · generic non-count
     Abstractions and mass nouns take no article in their generic sense: water,
     life, music, economics, happiness, advice. This is the single biggest source
     of article errors for Romance-language speakers.One exception worth knowing:
     in formal or literary English you can put a/an on an uncountable noun when
     you name a particular type of it, almost always with an adjective — a
     profound sadness, an excellent knowledge of history. (7.2)

[outGenA]  LEAF -> a / an   (rule 3.3)
  Question 3a · representative singular
     Picks out any arbitrary member to stand for the class. Slightly more formal
     than the plural, and it won't work with every predicate — A dog is
     widespread fails, because being widespread is true of the species and not of
     any individual.

[outGenThe]  LEAF -> the   (rule 3.4)
  Question 3a · the species
     Names the class as a single entity. Formal and mostly scientific: The blue
     whale is endangered. It does not work with every predicate — The tiger is
     endangered is fine, The tiger is everywhere is not. Note this reading is
     only reachable from Question 3.

[q4]  Question 4
  Q: Can my listener identify which one I mean?
  trail label: can the listener identify it?
     Work down the list. The first one that matches is your answer — they all
     produce the, and the labels just tell you why.
     -> out4a          4a · The sentence itself specifies it (the book I lent you · the man in the corner · the capital of Spain)
     -> out4b          4b · There's a superlative, ordinal or uniqueness word (the best · the first · the only · the same · the next)
     -> out4c          4c · We've mentioned it already (I bought a car. The car was red.)
     -> out4d          4d · It's inferable from something we mentioned (I bought a car. The engine was noisy.)
     -> out4e          4e · There's only one in the world (the sun · the equator · the internet)
     -> q4f            4f · There's only one in our shared community (the mall · the beach · the park · the gym · the doctor)
     -> out4g          4g · It's a role that belongs to something (the government · the president · the economy · the weather)
     -> q5             None of these — my listener can't tell which one

[out4a]  LEAF -> the   (rule 2.4)
  4a · specified by the sentence
     A relative clause (2.4.1), a prepositional phrase (2.4.2) or an of-phrase
     (2.4.3) narrows the noun to one referent, so the identification happens
     inside the sentence itself.Careful: a modifier alone is not enough. It has
     to make the referent identifiable. I met a woman who speaks Icelandic keeps
     a, because the clause describes her rather than picking out which woman is
     meant.

[out4b]  LEAF -> the   (rule 2.4.5)
  4b · superlative, ordinal or uniqueness word
     Best, first, only, same, next, last, main all entail that there's exactly
     one, so the follows automatically.

[out4c]  LEAF -> the   (rule 2.5)
  4c · second mention
     The classic a → the switch. First mention introduces, second mention points
     back.

[out4d]  LEAF -> the   (rule 2.6)
  4d · inferable from what we mentioned
     Part-whole and possession relations license this without any prior mention
     of the noun itself. A car has one engine, a room has one ceiling, so naming
     the whole makes the part identifiable.

[out4e]  LEAF -> the   (rule 2.3)
  4e · only one in the world
     Shared world knowledge does the identifying. No context needed at all.

[q4f]  Question 4f · check first
  Q: Does the noun name a place, or an institutional activity?
  trail label: a place, or an activity?
     This is where the mall and at school collide. Both are familiar community
     places, so the wrong branch is easy to take.
     -> out4f          A place (mall · beach · park · gym · bank · airport · library · store)
     -> outActivityZero An institutional activity or state (school · church · class · prison · court · bed · work · sea)
     WARNING: Compare at school, meaning studying, with at the school, meaning
     standing in the building. The activity set is closed and somewhat arbitrary
     — I'm at school is available but I'm at library isn't.

[out4f]  LEAF -> the   (rule 2.2)
  4f · only one in our shared community
     No specific one has been mentioned, and none needs to be. I'm at the mall
     doesn't identify which mall — it relies on your listener not needing to ask.
     This still holds for a mall neither of you has ever visited, because what's
     required is that the question which one? doesn't arise, not that a
     particular referent exists.

[outActivityZero]  LEAF -> no article   (rule 7.3)
  4f · institutional activity, not a place
     When the noun names the activity an institution exists for rather than its
     building, English drops the article: at school (studying), in prison
     (serving a sentence), in bed (sleeping), at work (working), in class, at
     sea, in court.Put the back the moment you mean the building instead: I
     parked at the school.

[out4g]  LEAF -> the   (rule 2.3)
  4g · a role that belongs to something
     Role nouns are inherently of something: government of a country, capital of
     a country, manager of a team. The article is licensed because the noun
     carries an implicit slot that context fills — and the slot can stay unfilled
     out loud. What should the government do? works between an American and a
     Spaniard discussing neither country, because it means the government of
     whatever situation we're discussing. Unique relative to an argument, not
     unique in the world.

[q5]  Question 5
  Q: How am I using the noun here — countable or not?
  trail label: countable, as used here?
     Ask about this use, not about the noun. Coffee and a coffee. Experience and
     an experience. Paper and a paper. A noun-property question sends
     dual-membership nouns down the wrong branch and keeps them there.
     -> out5a          Singular countable (I saw a dog. · She's a teacher. · I need a pen.)
     -> out5zPl        Plural countable (I bought books.)
     -> out5zNc        Non-count (We need water.)

[out5a]  LEAF -> a / an   (rule 2.1.2)
  Question 5 · indefinite singular
     Countable, singular, and your listener can't yet tell which one. Covers
     first mention, non-specific any uses, and classifying after be — She is a
     doctor (5.2).

[out5zPl]  LEAF -> no article   (rule 2.1.2)
  Question 5 · indefinite plural
     The plural counterpart of a. English has no plural indefinite article, so
     the slot stays empty. Add some if you need to signal quantity (Appendix 3).

[out5zNc]  LEAF -> no article   (rule 2.1.2)
  Question 5 · indefinite non-count
     Mass nouns take no article when indefinite. Add a quantifier if you need
     one: some water, a lot of water.
