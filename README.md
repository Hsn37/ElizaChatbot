# Slip parser for the script of Eliza

The chatbot is based on Slip. This is a parser for that language. The script contained is the default script for Eliza. Can be changed entirely.

**Instructions:**  
    Run ELIZA.py script in the console (open the console in the directory of the file and run *python ELIZA.py*).  
    It will launch the bot. You can type your messages in the console and the bot will respond there.  
    '>>>' is Eliza's response  
    '>' is your message  

# Script Layout
**Keywords**
1) initial = says this when it starts
2) final = says this when it quits
3) quit = if input is one of these, then quit
4) pre = substitutions (used in step 2)
5) post = substitutions (used in step 6)
6) synon = synonyms

**Logic:**
1) break down input into list of words
2) make pre subs
3) search for keywords, and make a list in descending order of priorities.
4) for each keyword, look for decomposition strings in the actual sentence. like substrings. if the substring is not present, move to the next keyword.
5) once decomp has been chosen, choose the reassembly pattern. cycle through the list of reassemblies.
6) make post subs
7) synonyms: work in decomp. signified by @. the word with @ is replaced with synonyms to see if decomp works or not.
8) (number) in reassembly: place the contents of the ith star from the actual sentence into the reassembly sentence.
9) $ symbol means this reassembly is saved and other keywords are searched first. if another keyword gives a sentence, go for it. otherwise choose a saved one. if no saved sentence, then simply make a recusrive call with the xnone keyword.

*more on the script instructions can be found here: http://chayden.net/eliza/instructions.txt*
